import oci
""" This is an example used in this article: https://mytechretreat.com/use-instance-principals-with-oci-python-sdk/ """

class OCICalls(object):
    def __init__(self):
    
        # generate signer
        self.generate_signer_from_instance_principals()

        # call apis
        self.get_compute_list()
    
    def generate_signer_from_instance_principals(self):
        try:
            # get signer from instance principals token
            self.signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        except Exception:
            print("There was an error while trying to get the Signer")
            raise SystemExit

        # generate config info from signer
        self.config = {'region': self.signer.region, 'tenancy': self.signer.tenancy_id}
        
    
    def get_compute_list(self):
        # initialize the IdentityClient with an empty config and only a signer
        identity_client = oci.identity.IdentityClient(config = {}, signer=self.signer )
        
        # initialize the ComputeClient with an empty config and only a signer
        compute_client = oci.core.ComputeClient(config = {}, signer=self.signer)
        
        # get the list of all compartments in my tenancy
        compartments = identity_client.list_compartments(self.config["tenancy"], compartment_id_in_subtree=True, access_level="ACCESSIBLE").data
         
        # find my compartment
        for compartment in compartments:
            if "test_compartment" in compartment.name:
                # get the list of all instances in my compartment
                instances = compute_client.list_instances(compartment.id).data
        
        print(f"My instances are: {instances}")
        
# Initiate process
OCICalls()