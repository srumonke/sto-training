# IaC Security: Terraform with misconfigurations for Checkov to find

provider "aws" {
  region = "ap-southeast-2"
}

# Issue: S3 bucket without encryption
resource "aws_s3_bucket" "data_bucket" {
  bucket = "hub24-customer-data"
  acl    = "public-read"  # Issue: Public access

  tags = {
    Name        = "Customer Data"
    Environment = "production"
  }
}

# Issue: No versioning enabled
resource "aws_s3_bucket_versioning" "data_bucket_versioning" {
  bucket = aws_s3_bucket.data_bucket.id
  versioning_configuration {
    status = "Disabled"
  }
}

# Issue: No server-side encryption
# (Missing aws_s3_bucket_server_side_encryption_configuration)

# Issue: No access logging
# (Missing aws_s3_bucket_logging)

# Issue: Security group with wide open ingress
resource "aws_security_group" "web_sg" {
  name        = "web-server-sg"
  description = "Security group for web servers"

  # Issue: Open to the world on all ports
  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Issue: Open egress
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Issue: RDS without encryption, public access, no backup
resource "aws_db_instance" "app_db" {
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "13.4"
  instance_class       = "db.t3.micro"
  identifier           = "hub24-app-db"
  username             = "admin"
  password             = "plaintext-password-123"  # Issue: Hardcoded password
  skip_final_snapshot  = true

  publicly_accessible    = true   # Issue: Public access
  storage_encrypted      = false  # Issue: No encryption
  backup_retention_period = 0     # Issue: No backups

  vpc_security_group_ids = [aws_security_group.web_sg.id]
}

# Issue: EC2 instance with no monitoring, public IP
resource "aws_instance" "web_server" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  associate_public_ip_address = true  # Issue: Public IP

  # Issue: No metadata service v2 enforcement
  # (Missing metadata_options block)

  # Issue: User data with secrets
  user_data = <<-EOF
    #!/bin/bash
    export DB_PASSWORD="plaintext-password-123"
    export API_KEY="sk_live_4eC39HqLyjWDarjtT1zdp7dc"
  EOF

  vpc_security_group_ids = [aws_security_group.web_sg.id]

  tags = {
    Name = "hub24-web-server"
  }
}
