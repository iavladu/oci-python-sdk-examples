import oci
from threading import Thread
""" This is an example used in this article: https://mytechretreat.com/how-to-prevent-http-429-toomanyrequests-errors-with-oci-python-sdk"""

class OCICalls(object):
    def __init__(self):
        self.regions = []
        
        # generate signer for authentication
        self.generate_signer_from_instance_principals()

        # call APIs
        self.get_regions()

        print(f"My regions are: {self.regions}")
        
    
    def generate_signer_from_instance_principals(self):
        try:
            # get signer from instance principals token
            self.signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        except Exception:
            print("There was an error while trying to get the Signer")
            raise SystemExit

        # generate config info from signer with region and tenancy_id
        self.config = {'region': self.signer.region, 'tenancy': self.signer.tenancy_id}
        
    
    def get_regions(self):
        # initialize the IdentityClient
        identity_client = oci.identity.IdentityClient(config = {}, signer=self.signer )
        
        jobs = []
        # get list of OCI subscribed regions 200 times so we break OCI's rate limiter
        for i in range(200):
            thread = Thread(target = self.__get_regions, args=(identity_client,))
            jobs.append(thread)
                            
        # start threads   
        for job in jobs:
            job.start()
            
        # join threads so we don't quit until all threads have finished
        for job in jobs:
            job.join()
        

    def __get_regions(self, identity_client):
        self.regions = identity_client.list_region_subscriptions(self.signer.tenancy_id).data


# Initiate process
OCICalls()