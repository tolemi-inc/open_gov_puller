from config_error import ConfigError


class Config:
    def __init__(
        self,
        category,
        dataset,
        citystate,
        open_gov_username,
        open_gov_password,
    ):
        self.category = category
        self.dataset = dataset
        self.citystate = citystate
        self.open_gov_username = open_gov_username
        self.open_gov_password = open_gov_password

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        if isinstance(value, str):
            self._category = value
        elif value is None:
            raise ConfigError("Missing category in config")
        else:
            raise ConfigError(
                "Expecting category to be a string value. Received: {} Fix config.".format(
                    value
                )
            )

    @property
    def dataset(self):
        return self._dataset

    @dataset.setter
    def dataset(self, value):
        if isinstance(value, str):
            self._dataset = value
        elif value is None:
            raise ConfigError("Missing dataset in config")
        else:
            raise ConfigError(
                "Expecting dataset to be a string value. Received: {} Fix config.".format(
                    value
                )
            )

    @property
    def citystate(self):
        return self._citystate

    @citystate.setter
    def citystate(self, value):
        if isinstance(value, str):
            self._citystate = value
        elif value is None:
            raise ConfigError("Missing citystate in config")
        else:
            raise ConfigError(
                "Expecting citystate to be a string value. Received: {} Fix config.".format(
                    value
                )
            )

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
