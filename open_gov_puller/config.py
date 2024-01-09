from config_error import ConfigError


class Config:
    def __init__(
        self,
        dataset,
        dataset_id,
        base_columns,
        additional_columns,
        login_url,
        request_url,
        open_gov_username,
        open_gov_password,
    ):
        self.dataset = dataset
        self.dataset_id = dataset_id
        self.base_columns = base_columns
        self.additional_columns = additional_columns
        self.login_url = login_url
        self.request_url = request_url
        self.open_gov_username = open_gov_username
        self.open_gov_password = open_gov_password

    @property
    def dataset(self):
        return self._dataset

    @dataset.setter
    def dataset(self, value):
        allowed_values = [
            "complaints",
            "building_permits",
            "demolition_permits",
            "electrical_permits",
            "equipment_permits",
            "plumbing_permits",
            "sign_permits",
        ]

        if value is None:
            raise ConfigError("Missing dataset in config")
        elif value in allowed_values:
            self._dataset = value
        else:
            raise ConfigError(
                "Invalid dataset: {}. Expecting one of {}".format(
                    value, ", ".join(allowed_values)
                )
            )

    @property
    def dataset_id(self):
        return self._dataset_id

    @dataset_id.setter
    def dataset_id(self, value):
        if isinstance(value, int):
            self._dataset_id = value
        elif value is None:
            raise ConfigError("Missing dataset id in config")
        else:
            raise ConfigError(
                "Expecting dataset id to be an integer value. Received: {} Fix config.".format(
                    value
                )
            )

    @property
    def base_columns(self):
        return self._base_columns

    @base_columns.setter
    def base_columns(self, value):
        if value is None:
            raise ConfigError("Missing base columns in config")
        else:
            self._base_columns = value

    @property
    def additional_columns(self):
        return self._additional_columns

    @additional_columns.setter
    def additional_columns(self, value):
        if value is None:
            raise ConfigError("Missing additional columns in config")
        else:
            self._additional_columns = value

    @property
    def login_url(self):
        return self._login_url

    @login_url.setter
    def login_url(self, value):
        if value is None:
            raise ConfigError("Missing login url in config")
        else:
            self._login_url = value

    @property
    def request_url(self):
        return self._request_url

    @request_url.setter
    def request_url(self, value):
        if value is None:
            raise ConfigError("Missing request url in config")
        else:
            self._request_url = value

    @property
    def open_gov_username(self):
        return self._open_gov_username

    @open_gov_username.setter
    def open_gov_username(self, value):
        if value is None:
            raise ConfigError("Missing open gov username in config")
        else:
            self._open_gov_username = value

    @property
    def open_gov_password(self):
        return self._open_gov_password

    @open_gov_password.setter
    def open_gov_password(self, value):
        if value is None:
            raise ConfigError("Missing open gov password in config")
        else:
            self._open_gov_password = value
