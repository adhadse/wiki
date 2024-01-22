# Terraform
Notes from freeCodeCamp course[^1].

[^1]: Created on January 21, 2024.

<iframe width="999" height="400" src="https://www.youtube.com/embed/SLB_c_ayRMo" title="Terraform Course - Automate your AWS cloud infrastructure" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

## What is Terraform?
Terraform is an infrastructure as code tool that lets you build, change and version cloud and on-premise resources.

It's built by HashiCorp.

!!!info Version Changes

    The Terraform file will have different structure depending on the version, Terraform `0.12` and earlier, & `0.13` and later.

    The following code will use `0.13` and later syntax and was tested with Terraform `v1.7.0`. The code demonstrated in the video and this wiki *might* not be same due to version updates!

## Installation
- You can follow the instructions mentioned on their developers page: [Install Terraform](https://developer.hashicorp.com/terraform/install).
- Installation on Windows:

    - Download the `.exe` file from `terraform.io/downloads.html` with appropriate architecture.
    Paste this file in `C:\Terraform\terraform.exe`
    - Update the *Path* in Environment Variables, by adding a *New* entry to the path: `C:\Terraform`.
    - Check the Terraform version from cmd: `terraform -v`. 

- Installation on Mac:

    - Using Homebrew by running `brew install terraform`.
    - Check the version using: `terraform -v`

- Installation on Linux:

    Run following commands (Fedora):
    ```bash
    sudo dnf install -y dnf-plugins-core
    sudo dnf config-manager --add-repo https://rpm.releases.hashicorp.com/fedora/hashicorp.repo
    sudo dnf -y install terraform
    ```

    Check the version using: `terraform -v`

## Install Terraform VSCode Extension
Go to VSCode extensions tab and install Terraform extension for all autocomplete features and syntax highlighting. Make sure it's from HashiCorp.

## Terraform overview
Let's create a new project and open in VSCode. All Terraform code is going to be stored in `.tf` extension file.

### Setup provider
Create a new file, naming it whatever you want, but make sure it's extension is `.tf`.

- Terraform provides many [providers](https://developer.hashicorp.com/terraform/language/providers) to interact with various [cloud service providers](https://registry.terraform.io/browse/providers), SaaS providers, and other APIs.

- On a per-user basis, per-project basis, Terraform will figure out which plugins need to be installed based off of the provider configuration in your Terraform file.

We'll try creating an AWS infrastructure in Terraform file. For that we can check the [AWS provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs) in Terraform registry.

```terraform
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
    }
  }
}

# Configure the AWS Provider & region
provider "aws" {
  region = "us-east-1"
}
```

### Setup Authentication
We'll try setting up bare minimum authentication, by [hard coding credentials](https://registry.terraform.io/providers/hashicorp/aws/latest/docs#provider-configuration) into the file.

!!!warning 

    Hard-coding credentials into any file that is meant to versioned by Version Control System and is going to be available for everybody to read is a **bad practice**. 

    This might leak the credentials.

We can set up credentials by adding it to `aws` provider block:

```terraform
# Configure the AWS Provider
provider "aws" {
  region = "us-east-1"
  access_key = "my-access-key"
  secret_key = "my-secret-key"
}
```

You can access them by clicking the profile name on top-right corner, and visiting **Security Credentials** and *Create access key*.

![AWS Console](/assets/images/cs/devops/terraform/aws-access-keys.png)

### Provision a resource within AWS
Regardless of what provider you're using, whether it's to create a resource on GCP/AWS/Azure (etc.), It's going to use the same exact syntax from a Terraform side.

The basic syntax is like this:
```terraform
# resource "<provider>_<resource_type>" "name" {  (1)
#   config options....  
#   key = "value"
#   key2 = "value2"
# }
```

1. Comments in Terraform files beings with a `#`

We'll walk through on how to deploy an EC2 (Elastic Compute Cloud) instance withing AWS, which is basically a compute instance/virtual machine withing AWS.

!!!note "Create EC2 instance via AWS console" 

    The [video](https://youtu.be/SLB_c_ayRMo?t=1865) go through creating AWS Instance via AWS console.

We'll use [aws_instance](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance) (*aws* is provider, *instance* is resource type) as the resource to configure:

```terraform hl_lines="1"
resource "aws_instance" "my-test-server" {
  ami           = "ami-0c7217cdde317cfec" # (1)!
  instance_type = "t2.micro"
}
```

1. The AMI (Amazon Machine Image) might change in the future, so do check the AMI in the console or in Docs. Stick to free-tier eligible for the duration of this tutorial.

Open a terminal tab in your editor and run `terraform init`.

- This will make Terraform to look at our config (`.tf` file(s)) and is going to look for all providers that we have defined.
- Right now, we have only specified one provider `aws`, so it's going to download the necessary plugins to interact with the AWS API. 

```bash
terraform init
```

You should see output something like this:

> Terraform has been successfully initialized!

The next command `terraform plan` command does sort for dry run of your code. It'll kind of show you, it's going to delete any instances, if it's going to create new instances, if it's going to modify instances. This make sure you don't accidantly break your production environment or anything else.

```bash
terraform plan
```

- The output is color coded so, green means new resource, red means deletion and orange implies modification to existing resource.

Lastly, we run 

```bash
terraform apply
```

Which will actually run our code, after you verify it, it will start provisioning the resources.

### Modify resources
Running the `terraform apply` *again* won't create another instance, <mark class="y">the reason being Terraform is written in declarative manner, which means we're not actually giving Terraform a bunch of steps to carry out.</mark> Instead, we're telling Terraform, what we want our infrastructure to look like.

<mark class="v">Terraform files are basically a blueprint of the infrastructure we want to have at the end.</mark>

Try running `terraform plan` for a sanity check, you'll see output something like this:

- `terraform plan` also talks to AWS and checks the state and gather information about it's state, if it's up or not.

```markdown
aws_instance.my-test-server: Refreshing state... [id=i-0eae7fc4ff618a32a]

No changes. Your infrastructure matches the configuration.

Terraform has compared your real infrastructure against your configuration and found no differences, so no changes are needed.
```

Running `terraform apply` will add this to the above output:

```
Apply complete! Resources: 0 added, 0 changed, 0 destroyed.
```

### Adding a tag

```terraform hl_lines="5 6 7"
resource "aws_instance" "my-test-server" {
  ami           = "ami-0c7217cdde317cfec" 
  instance_type = "t2.micro"

  tags = {
    Name = "fedora"
  }
}
```

And run `terraform plan` which should show you modification with tilde (~) marked with orange color about the tags.

```
aws_instance.my-test-server: Refreshing state... [id=i-0eae7fc4ff618a32a]

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  ~ update in-place

Terraform will perform the following actions:

  # aws_instance.my-test-server will be updated in-place
  ~ resource "aws_instance" "my-test-server" {
        id                                   = "i-0eae7fc4ff618a32a"
      ~ tags                                 = {
          + "Name" = "fedora"
        }
      ~ tags_all                             = {
          + "Name" = "fedora"
        }
        # (30 unchanged attributes hidden)

        # (8 unchanged blocks hidden)
    }

Plan: 0 to add, 1 to change, 0 to destroy.
```

And finally run `terraform apply` to apply the changes.

## Deleting Resources
To delete the resources we can run:

```bash
terraform destroy
```

<mark class="r">With `terraform destroy` it's going to destroy every single resource (whole infrastructure) that was created by Terraform</mark>. If you want to destroy a single resource there are other parameters that you need to pass in to make it work.

Instead, you can remove (or comment) the specific resource you want to be destroyed.

```terraform
# resource "aws_instance" "my-test-server" {
#   ami           = "ami-0c7217cdde317cfec" 
#   instance_type = "t2.micro"

#   tags = {
#     Name = "fedora"
#   }
# }
```

And hit `terraform apply` which will compare the state on AWS and state *declared* in your Terraform file and destroy the resource.

## Referencing Resources
Delete the resource you declared previously in the Terraform file, `my-test-server` and run `terraform apply`.

Let's explore how to create a VPC (Virtual Private Network) and subnet within that VPC. A VPC is a private, isolate network, within your AWS environment. Each one of the VPC by default is going to be isolated from one another. 

We'll use [aws_vpc](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc) resource.

```terraform
resource "aws_vpc" "my-test-vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "production"
  }
}
```

- The above block implies, for our VPC, the `10.0.0.0/16` is going to be the network that's going to be the network that's going to be used for that VPC.

We'll also want to create a subnet withing that VPC. For that we'll use [aws_subnet](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/subnet) resource.

```terraform hl_lines="2"
resource "aws_subnet" "subnet-1" {
  vpc_id     = aws_vpc.my-test-vpc.id
  cidr_block = "10.0.1.0/24" # (1)!

  tags = {
    Name = "prod-subnet"
  }
}
```

1. Make sure `cidr_block` of subnet falls within VPC's `cidr_block`

- To reference the `vpc_id` we use the resource `id` property which is defined for every resource, of the VPC we just created `my-test-vpc`.

Hit `terraform apply` and deploy the changes.

!!!note Terraform does not care about the order you define.

    Due to declarative nature of Terraform VPC **doesn't need** to declared before the subnet. Terraform will take care of what needs to get created first.

    Although, there are certain instances where it can't. In those case you can look at documentation to figure out a workaround.

## Terraform files
Let's talk about various files Terraform generates:

```bash
.
├── .terraform/
├── .terraform.loc.hcl
├── main.tf
├── terraform.tfstate
└── terraform.tfstate.backup
```

- When we did `terraform init` to initialize any plugins, it creates <mark class="y">the `.terraform/` directory and install all the required plugins in this directory.</mark> If you delete this dir, you can get it back just by running `terraform init`.
- <mark class="y">The `terraform.tfstate` represents whole state of Terraform.</mark> Anytime we create a resource withing any of the cloud provider, we need a way for Terraform to keep a track of what is created. **This file is very important, if this gets deleted, you'll break Terraform, causing a mismatched state between what's deployed and what's declared.**.

## Practice Project
In this section we'll create a new EC2 instance, assign it a public IP address, so that we can SSH into it a

1. Create a VPC
2. Create Internet Gateway

    So that we can send traffic out to the internet, 'cause we want to be able to assign a public IP address to this server so that anybody in the world can reach to it.

3. Create custom route table
4. Create a subnet
5. Associate subnet with Route table
6. Create security group to allow port `22`, `80` & `443`.
7. Create a network interface with an IP in the subnet that was created in step 4.
8. Assign an elastic IP to the network interface created in step 7.
9. Create Fedora server and install/enable apache2

The first thing we need to do is to create a [key pair](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html) within AWS. A key pair, consisting of a public key and a private key, is a set of security credentials that you use to prove your identity when connecting to an EC2 instance.<mark class="v">EC2 stores the public key on your instance, and you store private key</mark>. 

Checkout this [documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/create-key-pairs.html) on how to create a key-pair.

### Step 1: Create a VPC

```terraform
resource "aws_vpc" "prod-vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "production"
  }
}
```

### Step 2: Create a gateway
```terraform
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.prod-vpc.id
}
```

### Step 3: Create custom route table
```terraform
resource "aws_route_table" "prod-route-table" {
  vpc_id = aws_vpc.prod-vpc.id

  route {
    # cidr_block = "10.0.1.0/24"  (1)
    cidr_block   = "0.0.0.0/0" # (2)!
    gateway_id   = aws_internet_gateway.gw.id
  }

  route {
    ipv6_cidr_block        = "::/0"
    gateway_id             = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "prod"
  }
}
```

1. For the subnet `10.0.1.0/24` we're going to send it to the internet gateway.
2. We set up a default route, i.e., all traffic is going to get sent to the internet gateway.

### Step 4: Create a subnet

```terraform
resource "aws_subnet" "subnet-1" {
  vpc_id            =  aws_vpc.prod-vpc.id
  cidr_block        = "10.0.1.0/24"

  availability_zone = "us-east-1a"

  tags = {
    Name = "prod-subnet"
  }
}
```

### Step 5: Associate subnet with Route table
For this we'll use another resource type within Terraform called [route table association](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route_table_association)

```terraform
resource "aws_route_table_association" "a" {
  subnet_id      = aws_subnet.subnet-1.id
  route_table_id = aws_route_table.prod-route-table.id
}
```

### Step 6: Create a security group

```terraform
resource "aws_security_group" "allow_web" {
  name        = "allow_web_traffic"
  description = "Allow TLS inbound traffic and all outbound traffic"
  vpc_id      = aws_vpc.prod-vpc.id

  ingress {
    description      = "HTTPS"
    from_port        = 443             # (1)!
    to_port          = 443
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]   # (2)!
  }
  ingress {
    description      = "HTTP"
    from_port        = 80             
    to_port          = 80
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]  
  }
  ingress {
    description      = "SSH"
    from_port        = 22         
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]  
  }

  egress {
    from_port        = 0               # (3)!
    to_port          = 0
    protocol         = "-1"            # (4)!
    cidr_blocks      = ["0.0.0.0/0"]
  }

  tags = {
    Name = "allow_web"
  }
}
```

1. `from_port` and `to_port` allows us to specify port in specific range.
2. You can even specify a specific IP address, say you're work-computer so that only that can access it.
3. We're allowing all ports in the egress direction.
4. `-1` means any protocol

### Step 7: Create a Network Interface

```terraform
resource "aws_network_interface" "web-server-nic" {
  subnet_id       = aws_subnet.subnet-1.id
  private_ips     = ["10.0.1.50"]                     # (1)!
  security_groups = [aws_security_group.allow_web.id] # (2)!
}
```

1. What IP we need to give the server. We can choose any IP from the subnet except for those that AWS reserves a couple of addresses.
2. Pass in a list of security group.

### Step 8: Assign Elastic IP to NIC

```terraform
resource "aws_eip" "one" {
  domain                    = "vpc"
  network_interface         = aws_network_interface.web-server-nic.id
  associate_with_private_ip = "10.0.1.50"  # (1)!
  depends_on = [aws_internet_gateway.gw]  # (2)!
}
```

1. Reference the `private_ips` we assigned to our NIC, the IP we gave to the server.
2. Take a look at documentation for [`aws_eip`](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eip). We can use `depends_on` to set an explicit dependency on the Internet Gateway. **We want to reference the whole object, so no `id` here**.

<mark class="y">Deploying an elastic IP requires the Internet Gateway to be deployed first before the actual elastic IP gets deployed.</mark>

### Step 9: Create Fedora Server and install apache2

```terraform
resource "aws_instance" "web-server-instance" {
  ami                = "ami-081f29ca9a2a16cec"
  instance_type      = "t2.micro"
  availability_zone  = "us-east-1a"
  key_name           = "main-key"

  # another block
  network_interface {
    device_index = 0
    network_interface_id = aws_network_interface.web-server-nic.id
  }
  
  user_data = <<-EOF
              #!/bin/bash
              sudo dnf update -y
              sudo dnf install httpd -y
              sudo systemctl enable httpd.service
              sudo systemctl start httpd.service
              sudo bash -c 'echo you very first web server > /var/www/html/index.html'
              EOF   

  tags = {
    Name = "fedora-server"
  }
}
```

## Terraform Commands
You can just hit `terraform`, and it will list all terraform command available to execute.

We'll take a look at `terraform state` command.

```bash
# Will list all resources that we have state for
terraform state list
```

If you want to take a detailed look use `show` sub-command passing it the resource `id` shown in `state list` output:

```bash
terraform state show <resource_id>
```

## Terraform Output
What we could get Terraform to automatically print resources properties out when we run a `terraform apply`, i.e, when the resource is created?

We can try this let's say when we want to extract the public IP, that's going to get assigned to an elastic IP or an EC2 instance that gets created.

```terraform
output "server_public_ip" {
  value = aws_eip.one.public_ip  # (1)!
}
```

1. You can get the property you want to show from `terraform state show` sub-command.

Next time, when you'll run `terraform apply` it will print the property for you, instead of you having to manually go and check it either via AWS Console or via Terraform `state` command.

!!!tip "use `--auto-approve` with `terraform apply` to automatically approve the changes"

    Use carefully though!

If you do add `output` but don't want to run `terraform apply`, because it can potentially make changes to your network. In production environment, you don't want to accidentally deploy or delete something, but just to see what the output is.

In that case, you should use:

```bash
terraform refresh
```

Which refreshes all of your state, and it'll run the outputs. So, you can verify them without actually having to apply anything.

## Target Resources
Maybe you just wanted to delete an individual resource or if you're trying to roll out with a deployment to do staged deployments, where only certain resources are to be deployed one day. And then the next day, another set of resources.

We can individually target the resources in our config by passing a `-target` flag.

Let's say we want to destroy the web server, we can run:

```bash
terraform destroy -target aws_instance.web-server-instance
```

and to redeploy it:

```bash
terraform apply -target aws_instance.web-server-instance
```

## Variables
Terraform allows us to use variables so that we can reuse values throughout our code without having to repeat ourselves.

Let's say we want to take `cidr_block` definition for `subnet-1` and store it in a variable.

```terraform hl_lines="3"
resource "aws_subnet" "subnet-1" {
  vpc_id = aws_vpc.prod-vpc.id
  cidr_block = "10.0.1.0/24"

  availability_zone = "us-east-1a"

  tags = {
    Name = "prod-subnet"
  }
}
```

You can do it like this:

```terraform
variable "subnet_prefix" {   # (1)!
  description = "cidr block for the subnet"
  default     = "10.0.66.0/24" # (2)!
  type        = string # (3)!
}
```

1. Either we can leave this block empty or provide optional values, which are `description`, `default` & `type`.
2. If user doesn't specify a default value, use the default one.
3. We can type constrain it, so when a user enters in a value, we can make sure that they enter the proper type for this. Take a look at [Types and Values](https://developer.hashicorp.com/terraform/language/expressions/types)

To reference it we use it something like this:


```terraform
resource "aws_subnet" "subnet-1" {
  vpc_id = aws_vpc.prod-vpc.id
  cidr_block = var.subnet_prefix

  availability_zone = "us-east-1a"

  tags = {
    Name = "prod-subnet"
  }
}
```

When we hit `terraform apply`, Terraform will ask you to enter the value, since the var has not been assigned a value.

- Another way we can assign it a value is using command line arguments.

```bash
terraform apply -var "subnet_prefix=10.0.100.0/24"
```

- The best way would be to use separate file to assign a variable.

<mark class="y">Terraform looks for `terraform.tfvars` for variable assignments. We can keep our vars in this file as:</mark>

```terraform
subnet_prefix="10.0.100.0/24"
```

And when you run `terraform apply`, it won't ask you for the variable assignment and instead take it from this file.

### Multiple `.tfvars` files?
We can pass in the filename to look into for vars like this:

```bash
terraform apply -var-file example.tfvars
```

### Using list as a variable.
Let's say our `terraform.tfvars` looks like this:

```terraform
subnet_prefix=["10.0.1.0/24", "10.0.2.0/24]
```

and Terraform file like:

```terraform hl_lines="16 27"
# provider config...

resource "aws_vpc" "prod-vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "production"
  }
}

variable "subnet_prefix" {  
  description = "cidr block for the subnet"
}

resource "aws_subnet" "subnet-1" {
  vpc_id = aws_vpc.prod-vpc.id
  cidr_block = var.subnet_prefix[0]

  availability_zone = "us-east-1a"

  tags = {
    Name = "prod-subnet-1"
  }
}

resource "aws_subnet" "subnet-2" {
  vpc_id = aws_vpc.prod-vpc.id
  cidr_block = var.subnet_prefix[1]

  availability_zone = "us-east-1a"

  tags = {
    Name = "prod-subnet-2"
  }
}
```

### Using objects within variables
We'll change the way we assign the tag. Instead, of assigning the tag or hard coding it, we want to have a variable/object that has two properties, `cidr_block` and `name` property.

In our `terraform.tfvars`:

```terraform
subnet_prefix = [
  { cidr_block = "10.0.1.0/24", name = "prod-subnet"}, 
  { cidr_block = "10.0.2.0/24", name = "dev_subnet"}
]
```

And so our Terraform file will look something like:

```terraform hl_lines="16 21 27 32"
# provider config...

resource "aws_vpc" "prod-vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "production"
  }
}

variable "subnet_prefix" {  
  description = "cidr block for the subnet"
}

resource "aws_subnet" "subnet-1" {
  vpc_id = aws_vpc.prod-vpc.id
  cidr_block = var.subnet_prefix[0].cidr_block

  availability_zone = "us-east-1a"

  tags = {
    Name = var.subnet_prefix[0].name
  }
}

resource "aws_subnet" "subnet-2" {
  vpc_id = aws_vpc.prod-vpc.id
  cidr_block = var.subnet_prefix[1].cidr_block

  availability_zone = "us-east-1a"

  tags = {
    Name = var.subnet_prefix[1].name
  }
}
```AKIA3HFXV3NBTRFZRZOI