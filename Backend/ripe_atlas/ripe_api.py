import requests

RIPE_BASE_URL = "https://atlas.ripe.net/api/v2/"
MEASUREMENTS_URL = RIPE_BASE_URL + "measurements/"
MY_MEASUREMENTS_URL = MEASUREMENTS_URL + "my/"
CURRENT_PROBES_URL = RIPE_BASE_URL + "credits/income-items/"
ANCHORS_URL = RIPE_BASE_URL + "anchors/"
PROBES_URL = RIPE_BASE_URL + "probes/"

# fields should be comma seperated for the fields query parameter, id and type is always included
WANTED_PROBE_FIELDS = "id,type,is_anchor,address_v4,address_v6,asn_v4,asn_v6,geometry,prefix_v4,prefix_v6,description"
WANTED_MEASUREMENT_FIELDS = "id,type,description,target_ip"

# the type of  measurements that we can put an alert on
SUPPORTED_TYPE_MEASUREMENTS = ('ping',)


def is_token_valid(token: str) -> bool:
    response = requests.get(url=RIPE_BASE_URL + "credits/income-items", params={'key': token})
    if response.status_code == 403:
        if response.json()['error']['detail'] == 'The provided API key does not exist':
            return False
    else:
        return True


class RipeUserData:
    def __init__(self, token):
        self.token: str = token
        self.user_defined_measurements: list = self.get_user_defined_measurements()

    def get_probe_information(self, url=None, probe_id=None) -> dict:

        # status: 1, means we are only interested in probes that are connected.
        params = {"key": self.token, "fields": WANTED_PROBE_FIELDS, "status": 1}

        if probe_id:
            url = PROBES_URL + f"{probe_id}"
        response = requests.get(url, params=params).json()

        # probes data dont have a 'host' key, but the description refers to the host in most cases
        response['host'] = response.pop('description')
        return response

    def get_probes_by_host(self, host) -> list:

        params = {'search': host, 'include': 'probe', 'key': self.token}

        # probes can be found by host via the anchors api.
        response = requests.get(url=ANCHORS_URL, params=params).json()

        if response.get('results') is None:
            raise ValueError

        results = response['results']
        probes = []

        for result in results:
            probe = result['probe']
            probe = {field: probe[field] for field in WANTED_PROBE_FIELDS.split(',')}
            probe['host'] = probe.pop("description")
            probes.append(probe)
        return probes

    def get_probes_by_prefix(self, prefix) -> list:

        probes: list = []
        is_ip_v4: bool = "." in prefix

        if is_ip_v4:
            params = {'prefix_v4': prefix, 'fields': WANTED_PROBE_FIELDS, 'key': self.token}
        else:
            params = {'prefix_v6': prefix, 'fields': WANTED_PROBE_FIELDS, 'key': self.token}

        response: dict = requests.get(url=PROBES_URL, params=params).json()

        if response.get('results') is None:
            raise ValueError

        for probe in response['results']:
            probe['host'] = probe.pop("description")
            probes.append(probe)

        return probes

    def get_probes_by_asn(self, asn) -> list:

        probes: list = []
        params = {'asn': asn, 'fields': WANTED_PROBE_FIELDS, 'key': self.token}
        response = requests.get(url=RIPE_BASE_URL + "/probes", params=params).json()

        if response.get('results') is None:
            raise ValueError

        for probe in response['results']:
            probe['host'] = probe.pop("description")
            probes.append(probe)

        return probes

    def get_anchoring_measurements(self, target_address: str) -> list:

        params = {
            'key': self.token,
            'tags': 'anchoring',
            'status': 'Ongoing',
            'target_ip': target_address,
            'fields': WANTED_MEASUREMENT_FIELDS
        }
        response = requests.get(MEASUREMENTS_URL, params=params).json()

        return [measurement for measurement in response['results'] if
                measurement['type'] in SUPPORTED_TYPE_MEASUREMENTS]

    def get_user_defined_measurements(self):

        params = {
                "key": self.token,
                "status": "Ongoing",
                "fields": WANTED_MEASUREMENT_FIELDS
        }
        response = requests.get(MY_MEASUREMENTS_URL, params=params).json()
        return [measurement for measurement in response['results'] if
                measurement['type'] in SUPPORTED_TYPE_MEASUREMENTS]

    def get_alertable_user_measurements_target(self, ip_address: str) -> list:

        if len(self.user_defined_measurements) > 0:
            return [measurement for measurement in self.user_defined_measurements
                    if measurement['target_ip'] == ip_address]
        else:
            return []

    def get_alertable_measurements_probe(self, probe: dict) -> dict:
        """Get alertable measurements that target probe"""

        relevant_measurements = {
            "anchoring_measurements": [],
            "user_defined_measurements": []
        }

        ip_v4 = probe.get("address_v4")
        ip_v6 = probe.get("address_v6")
        is_anchor = probe.get("is_anchor")

        if ip_v4:
            if is_anchor:
                relevant_measurements['anchoring_measurements'].extend(self.get_anchoring_measurements(ip_v4))
            relevant_measurements['user_defined_measurements'].extend(
                self.get_alertable_user_measurements_target(ip_v4))

        if ip_v6:
            if is_anchor:
                relevant_measurements['anchoring_measurements'].extend(self.get_anchoring_measurements(ip_v6))
            relevant_measurements['user_defined_measurements'].extend(
                self.get_alertable_user_measurements_target(ip_v6))

        return relevant_measurements

    def get_owned_anchors_probes(self) -> dict:

        anchors_and_probes: dict = {"anchors": [], "probes": []}
        response = requests.get(url=CURRENT_PROBES_URL, params={'key': self.token}).json()
        income_groups: dict = response['groups']
        income_sources: list = [*income_groups['hosted_probes'], *income_groups['sponsored_probes'],
                                *income_groups['ambassador_probes'], *income_groups['hosted_anchors'],
                                *income_groups['sponsored_anchors']]

        for income in income_sources:
            probe_information = self.get_probe_information(url=income['probe'])

            # add related measurements to probe
            probe_information.update(self.get_alertable_measurements_probe(probe_information))

            if probe_information['is_anchor']:
                anchors_and_probes['anchors'].append(probe_information)
            else:
                anchors_and_probes['probes'].append(probe_information)

        return anchors_and_probes

    def search_probes(self, filter, value) -> list:

        anchors_and_probes: dict = {"anchors": [], "probes": []}
        try:
            if filter == "probe_id":
                probes = [self.get_probe_information(probe_id=value)]
            elif filter == "host":
                probes = self.get_probes_by_host(value)
            elif filter == "prefix":
                probes = self.get_probes_by_prefix(value)
            elif filter == "asn":
                probes = self.get_probes_by_asn(value)
            else:
                raise ValueError
        except ValueError:
            raise ValueError

        if probes:
            for probe in probes:
                probe.update(
                    self.get_alertable_measurements_probe(probe))
                if probe['is_anchor']:
                    anchors_and_probes['anchors'].append(probe)
                else:
                    anchors_and_probes['probes'].append(probe)

        return anchors_and_probes
