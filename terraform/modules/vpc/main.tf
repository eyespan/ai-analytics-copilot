#vpc
resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(local.common_tags, {
    Name = "${var.name}-vpc"
  })
}

#internet gateway
resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags = merge(local.common_tags, {
    Name = "${var.name}-igw"
  })
}

#public subnets

resource "aws_subnet" "public" {
  for_each = var.public_subnets

  vpc_id                  = aws_vpc.this.id
  cidr_block              = each.value.cidr
  availability_zone       = each.value.az
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name                                        = "${var.name}-public-${each.key}",
    "kubernetes.io/role/elb"                    = "1",
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  })
}


#private subnet
resource "aws_subnet" "private" {
  for_each = var.private_subnets

  vpc_id            = aws_vpc.this.id
  cidr_block        = each.value.cidr
  availability_zone = each.value.az

  tags = merge(local.common_tags, {
    Name                                        = "${var.name}-private-${each.key}",
    "kubernetes.io/role/internal-elb"           = "1",
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  })
}


#elastic ip
resource "aws_eip" "nat" {
  count  = var.single_nat_gateway ? 1 : 0
  domain = "vpc"

  tags = merge(local.common_tags, {
    Name = "${var.name}-nat-eip"
  })
}

#nat gateway
resource "aws_nat_gateway" "this" {
  count = var.single_nat_gateway ? 1 : 0

  allocation_id = aws_eip.nat[0].id

  # safest choice: pick first public subnet deterministically
  subnet_id = values(aws_subnet.public)[0].id

  depends_on = [aws_internet_gateway.this]

  tags = merge(local.common_tags, {
    Name = "${var.name}-nat"
  })
}


#public route table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }

  tags = merge(local.common_tags, {
    Name = "${var.name}-public-rt"
  })
}

#private route table
resource "aws_route_table" "private" {
  for_each = var.private_subnets

  vpc_id = aws_vpc.this.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.this[0].id
  }

  tags = merge(local.common_tags, {
    Name = "${var.name}-private-rt-${each.key}"
  })
}


#public route association
resource "aws_route_table_association" "public" {
  for_each = aws_subnet.public

  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}

#private route association
resource "aws_route_table_association" "private" {
  for_each = aws_subnet.private

  subnet_id      = each.value.id
  route_table_id = aws_route_table.private[each.key].id
}


