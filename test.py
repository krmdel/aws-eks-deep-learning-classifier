import requests
import subprocess
import os

def get_loadbalancer_endpoint():
    """Get the LoadBalancer endpoint from Kubernetes"""
    try:
        result = subprocess.run(
            ['kubectl', 'get', 'svc', 'clothing-classifier', 
             '-o', 'jsonpath={.status.loadBalancer.ingress[0].hostname}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception as e:
        print(f"Could not get LoadBalancer endpoint: {e}")
    return None

# Option 1: Use LoadBalancer endpoint (for EKS)
lb_endpoint = get_loadbalancer_endpoint()
if lb_endpoint:
    url = f'http://{lb_endpoint}/predict'
    print(f"Using LoadBalancer endpoint: {lb_endpoint}")
else:
    # Fallback: Use environment variable or default
    url = os.getenv('SERVICE_URL', 'http://localhost:8080/predict')
    print(f"Using fallback URL: {url}")
    print("Note: If using LoadBalancer, wait a few minutes for DNS to propagate")
    print("Or use port-forward: kubectl port-forward service/clothing-classifier 8080:80")

# Option 2: Use port-forward (for local testing)
# First run: kubectl port-forward service/clothing-classifier 8080:80
# Then uncomment: url = 'http://localhost:8080/predict'

# Option 3: Use NodePort with node IP (if security group allows)
# url = 'http://100.48.44.32:30080/predict'

request = {
    "url": "http://bit.ly/mlbookcamp-pants"
}

response = requests.post(url, json=request)
result = response.json()

print(f"Top prediction: {result['top_class']} ({result['top_probability']:.2%})")
print(f"\nAll predictions:")
for cls, prob in result['predictions'].items():
    print(f"  {cls:12s}: {prob:.2%}")