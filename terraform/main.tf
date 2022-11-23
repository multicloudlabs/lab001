terraform {
  required_providers {
    ibm = {
      source = "IBM-Cloud/ibm"
      version = ">= 1.12.0"
    }
  }
}

provider ibm {
  ibmcloud_api_key      = var.ibmcloud_api_key
  region                = var.region
  ibmcloud_timeout      = 60
}

data ibm_is_image s390x_image {
    name = var.s390x_image
}

data ibm_is_image x86-64_image {
    name = var.x86-64_image
}


resource ibm_resource_group group {
  name = "${var.rg_prefix}-${var.id}"
}

resource ibm_is_vpc vpc {
    name = "${var.vpc_prefix}-${var.id}"
    resource_group = ibm_resource_group.group.id
}

resource "ibm_is_subnet" "subnet" {
  name            = "${var.subnet_prefix}-${var.zone}-${var.id}"
  vpc             = ibm_is_vpc.vpc.id
  zone            = var.zone
  ipv4_cidr_block = "${var.subnet_ip_range}"
  resource_group = ibm_resource_group.group.id
}

resource ibm_is_ssh_key ssh_key {
  name       = "${var.ssh_key_prefix}-${var.id}"
  public_key = var.ssh_public_key
  resource_group = ibm_resource_group.group.id
}

resource ibm_is_instance s390x_vsi01 {
  name           = "vsi-s390x-01"
  image          = data.ibm_is_image.s390x_image.id
  profile        = var.s390x_machine_type
  resource_group = ibm_resource_group.group.id

  primary_network_interface {
    subnet   = ibm_is_subnet.subnet.id
    security_groups = [ibm_is_security_group.allow_all.id]
  }  

  user_data  = file("${path.module}/config/vsi-s390x-01.sh")
                 
  vpc        = ibm_is_vpc.vpc.id
  zone       = var.zone

  keys       = [ibm_is_ssh_key.ssh_key.id]
}

resource ibm_is_instance s390x_vsi02 {
  name           = "vsi-s390x-02"
  image          = data.ibm_is_image.s390x_image.id
  profile        = var.s390x_machine_type
  resource_group = ibm_resource_group.group.id

  primary_network_interface {
    subnet   = ibm_is_subnet.subnet.id
    security_groups = [ibm_is_security_group.allow_all.id]
  }  
  user_data  = file("${path.module}/config/vsi-s390x-02.sh")
                 
  vpc        = ibm_is_vpc.vpc.id
  zone       = var.zone

  keys       = [ibm_is_ssh_key.ssh_key.id]
}


resource ibm_is_instance x86-64_vsi {
  name           = "vsi-x86-64-01"
  image          = data.ibm_is_image.x86-64_image.id
  profile        = var.x86-64_machine_type
  resource_group = ibm_resource_group.group.id

  primary_network_interface {
    subnet   = ibm_is_subnet.subnet.id
    security_groups = [ibm_is_security_group.allow_all.id]
  }  

  user_data  = file("${path.module}/config/vsi-x86-64-01.sh")
                 
  vpc        = ibm_is_vpc.vpc.id
  zone       = var.zone

  keys       = [ibm_is_ssh_key.ssh_key.id]
}

resource ibm_is_floating_ip s390x_vsi01_fip {
  name   = "fip-${var.id}-vsi-01"
  target = ibm_is_instance.s390x_vsi01.primary_network_interface.0.id
}

resource ibm_is_floating_ip s390x_vsi02_fip {
  name   = "fip-${var.id}-vsi-02"
  target = ibm_is_instance.s390x_vsi02.primary_network_interface.0.id
}

resource ibm_is_floating_ip x86-64_vsi_fip {
  name   = "fip-${var.id}-vsi-03"
  target = ibm_is_instance.x86-64_vsi.primary_network_interface.0.id
}


resource ibm_is_security_group allow_all {
  name           = "sg-${var.id}-allow-all"
  resource_group = ibm_resource_group.group.id
  vpc            = ibm_is_vpc.vpc.id
}

resource ibm_is_security_group_rule ingress {
  direction = "outbound"
  group     = ibm_is_security_group.allow_all.id
  remote    = "0.0.0.0/0"
}

resource ibm_is_security_group_rule egress {
  direction = "inbound"
  group     = ibm_is_security_group.allow_all.id
  remote    = "0.0.0.0/0"
}

output s390x_vsi01 {
  value = {
  id           = ibm_is_instance.s390x_vsi01.id,
  ipv4_address = ibm_is_floating_ip.s390x_vsi01_fip.address}
}

output s390x_vsi02 {
  value = {
  id           = ibm_is_instance.s390x_vsi02.id,
  zone         = ibm_is_instance.s390x_vsi02.zone,
  ipv4_address = ibm_is_floating_ip.s390x_vsi02_fip.address}
}

output x86-64_vsi {
  value = {
  id           = ibm_is_instance.x86-64_vsi.id
  ipv4_address = ibm_is_floating_ip.x86-64_vsi_fip.address }
}
