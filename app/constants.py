class COLLECTOR_NAMES:
    SCRAPER = "scraper"
    WHOIS = "whois"
    ALL = [SCRAPER, WHOIS]


class COLLECTOR_STATUSES:
    ACTIVE = True
    INACTIVE = False


class ERRORS:
    INVALID_COLLECTOR = "Invalid collector name"
    NOT_FQDM = "Is not FQDM(Fully Qualified Domain Name)"
    CREATING_JOB_FOR_DISABLED_COLLECTOR = "Creating job for inactive collector"


class COLLECTOR_JOB_STATUSES:
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
