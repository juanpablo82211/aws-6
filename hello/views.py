import boto3
import uuid
from django.shortcuts import render, redirect

# Clientes AWS
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
tabla = dynamodb.Table('Usuario')

s3 = boto3.client('s3', region_name='us-east-1')
rekognition = boto3.client('rekognition', region_name='us-east-1')

# Diccionario ejemplo de alimentos con sus calorías (ajusta o extiende)
ALIMENTOS_CALORIAS = {
    'Pizza': 500,
    'Burger': 400,
    'Apple': 95,
    # Agrega más alimentos y calorías según necesites
}

def user_dashboard(request):
    usuario_id = request.GET.get('usuario_id')  # debe ser usuario_id para coincidir con URL y select
    if not usuario_id:
        # Si no hay usuario_id, muestra la selección de usuarios
        # Carga todos los usuarios para mostrar en el select
        response = tabla.scan()
        usuarios = response.get('Items', [])
        return render(request, 'hello/dashboard.html', {'usuarios': usuarios})

    # Obtén los datos del usuario
    datos = tabla.get_item(Key={'usuario_id': usuario_id}).get('Item')
    if not datos:
        return render(request, 'hello/dashboard.html', {'error': 'Usuario no encontrado.'})

    if request.method == 'POST' and 'imagen' in request.FILES:
        imagen = request.FILES['imagen']
        nombre_archivo = f"{usuario_id}_{uuid.uuid4()}.jpg"
        bucket = 'my-calorias.bucket'  # Cambia por tu bucket real

        # Subir a S3
        s3.upload_fileobj(imagen, bucket, nombre_archivo)

        # Llamar a Rekognition
        response = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': nombre_archivo}},
            MaxLabels=5,
            MinConfidence=70
        )

        labels_detectadas = [label['Name'] for label in response['Labels']]
        calorias_detectadas = 0
        for label in labels_detectadas:
            if label in ALIMENTOS_CALORIAS:
                calorias_detectadas = ALIMENTOS_CALORIAS[label]
                break

        if calorias_detectadas > 0:
            # Actualiza las calorías restando las detectadas, asegurando que no baje de 0
            nueva_calorias = max(datos.get('calorias', 0) - calorias_detectadas, 0)
            tabla.update_item(
                Key={'usuario_id': usuario_id},
                UpdateExpression='SET calorias = :c',
                ExpressionAttributeValues={':c': nueva_calorias}
            )
            datos['calorias'] = nueva_calorias

    return render(request, 'hello/dashboard.html', {
        'usuario': datos,
        'usuarios': tabla.scan().get('Items', [])  # para el select en la página
    })


def crear_usuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        calorias = int(request.POST.get('calorias', '2000'))

        usuario_id = str(uuid.uuid4())
        tabla.put_item(Item={
            'usuario_id': usuario_id,
            'nombre': nombre,
            'calorias': calorias
        })

        return redirect(f"/?usuario_id={usuario_id}")

    return render(request, 'hello/crear_usuario.html')
