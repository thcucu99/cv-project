import vat.utils.turk.quals.qual_utils as qual_utils
import vat.utils.turk.quals.requirement_utils as requirement_utils
from vat.utils.turk.connection import get_client

from typing import Union, List


class Qualification(object):
    def __init__(self, qualification_type_id: str, sandbox: bool):
        self.qualification_type_id = qualification_type_id
        self.client = get_client(sandbox=sandbox)
        return

    def check_if_worker_has_qual(self, worker_id:str) -> bool:
        has, granttime = qual_utils.check_if_worker_has_qual(
            client=self.client,
            qualification_type_id=self.qualification_type_id,
            worker_id=worker_id,
        )

        return has

    @staticmethod
    def create_qualification(sandbox: bool, name: str, description: str):
        client = get_client(sandbox=sandbox)
        qualification_type_id = qual_utils.create_qualification(
            client=client,
            qual_name=name,
            description=description,
        )
        print(qualification_type_id)
        return qualification_type_id

    def grant_qualification(self, worker_id: str, send_notification=False, value=1):
        qual_utils.grant_qualification(
            client=self.client,
            qualification_type_id=self.qualification_type_id,
            worker_id=worker_id,
            value=value,
            send_notification=send_notification,
        )

    def revoke_qualification(
            self,
            worker_id:str,
    ):

        qual_utils.revoke_qualification(
            client=self.client,
            worker_id=worker_id,
            qualification_type_id=self.qualification_type_id,
        )

    def list_workers(self):
        worker_ids = qual_utils.list_workers_with_qual(
            client=self.client,
            qualification_type_id=self.qualification_type_id,
        )
        return worker_ids

    def make_requirement(
            self,
            require_worker_has_qual: bool,
    )->dict:
        requirement = requirement_utils.make_qual_exists_requirement(
            client=self.client,
            exists=require_worker_has_qual,
            qualification_type_id=self.qualification_type_id,
        )

        return requirement

    def make_bounds_requirement(
            self,
            value_min: Union[type(None), int],
            value_max: Union[type(None), int],
    ) -> List[dict]:
        requirement = requirement_utils.make_qual_comparator_requirements(
            client=self.client,
            lower_bound=value_min,
            upper_bound=value_max,
            qualification_type_id=self.qualification_type_id,
        )

        return requirement

    def get_value(self, worker_id: str):
        return qual_utils.get_current_qual_value(
            client=self.client,
            worker_id=worker_id,
            qualification_type_id=self.qualification_type_id,
            verbose=False,
        )

    def set_value(self, worker_id: str, value: int):
        qual_utils.set_qual_value(
            client=self.client,
            worker_id=worker_id,
            qualification_type_id=self.qualification_type_id,
            value=value,
        )


class NotNaiveQualification(Qualification):
    def __init__(self, ):
        sandbox = False
        from vat.utils.turk.quals import NOT_NAIVE_TYPE_ID
        qualification_type_id = NOT_NAIVE_TYPE_ID
        super().__init__(qualification_type_id, sandbox)
