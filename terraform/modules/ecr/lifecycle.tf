resource "aws_ecr_lifecycle_policy" "this" {

  for_each = aws_ecr_repository.this

  repository = each.value.name

  policy = jsonencode({

    rules = [

      {

        rulePriority = 1

        description = "Keep latest 20 images"

        selection = {

          tagStatus = "any"

          countType = "imageCountMoreThan"

          countNumber = var.max_image_count

        }

        action = {

          type = "expire"

        }

      }

    ]

  })

}