import oci
from threading import Thread
""" This is an example used in this article: https://mytechretreat.com/how-to-prevent-http-429-toomanyrequests-errors-with-oci-python-sdk"""

class OCICalls(object):
    def __init__(self):
        ### Create Custom Retry Strategy ###
        ####################################
        self.custom_retry_strategy = oci.retry.RetryStrategyBuilder(
        # Whether to enable a check that we don't exceed a certain number of attempts
        max_attempts_check=True,
        # check that will retry on connection errors, timeouts and service errors 
        service_error_check=True,
        # a check that we don't exceed a certain amount of time retrying
        total_elapsed_time_check=True,
        # maximum number of attempts
        max_attempts=10,
        # don't exceed a total of 900 seconds for all calls
        total_elapsed_time_seconds=900,
        # if we are checking o service errors, we can configure what HTTP statuses to retry on
        # and optionally whether the textual code (e.g. TooManyRequests) matches a given value
        service_error_retry_config={
            400: ['QuotaExceeded', 'LimitExceeded'],
            429: []
        },
        # whether to retry on HTTP 5xx errors
        service_error_retry_on_any_5xx=True,
        # Used for exponention backoff with jitter
        retry_base_sleep_time_seconds=2,
        # Wait 60 seconds between attempts
        retry_max_wait_between_calls_seconds=60,
        # the type of backoff
        # Accepted values are: BACKOFF_FULL_JITTER_VALUE, BACKOFF_EQUAL_JITTER_VALUE, BACKOFF_FULL_JITTER_EQUAL_ON_THROTTLE_VALUE
        backoff_type=oci.retry.BACKOFF_FULL_JITTER_EQUAL_ON_THROTTLE_VALUE
        ).get_retry_strategy()
        ####################################

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
        self.regions = identity_client.list_region_subscriptions(self.signer.tenancy_id, retry_strategy=self.custom_retry_strategy).data


# Initiate process
OCICalls()