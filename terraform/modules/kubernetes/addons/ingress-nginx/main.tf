resource "helm_release" "ingress_nginx" {

  name = "ingress-nginx"

  repository = "https://kubernetes.github.io/ingress-nginx"

  chart = "ingress-nginx"

  namespace = "ingress-nginx"

  create_namespace = false

  version = "4.12.2"

  values = [
    yamlencode({
      controller = {

        replicaCount = 2

        service = {
          type = "LoadBalancer"
        }

        metrics = {
          enabled = true
        }
      }
    })
  ]
}