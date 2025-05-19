import requests
import time
import sys

def simulate_call(room, bed):
    """Simulate a patient call from a specific room and bed"""
    print(f"Simulando llamada desde habitación {room}, cama {bed}...")
    
    # Make the call request
    call_url = f"http://localhost:5000/llamada/{room}/{bed}"
    response = requests.get(call_url)
    
    if response.status_code == 200:
        print("Llamada registrada correctamente.")
        print("Esperando 10 segundos para simular atención...")
        time.sleep(10)
        
        # Simulate attention
        attend_url = "http://localhost:5000/atender/1"  # This would normally be the actual call ID
        print("Simulando atención (esto normalmente se haría a través del enlace en la notificación)...")
        print(f"URL de atención: {attend_url}")
        
        print("Esperando 10 segundos para simular presencia...")
        time.sleep(10)
        
        # Simulate presence
        presence_url = f"http://localhost:5000/presencia/{room}/{bed}"
        print(f"Simulando presencia en habitación {room}, cama {bed}...")
        presence_response = requests.get(presence_url)
        
        if presence_response.status_code == 200:
            print("Presencia registrada correctamente.")
        else:
            print(f"Error al registrar presencia: {presence_response.status_code}")
            print(presence_response.text)
    else:
        print(f"Error al registrar llamada: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python test_call.py <habitación> <cama>")
        print("Ejemplo: python test_call.py 101 a")
        sys.exit(1)
    
    room = sys.argv[1]
    bed = sys.argv[2]
    
    simulate_call(room, bed) 