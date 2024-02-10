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

    INVALID_STATUS_FOR_COLLECTOR_JOB = "Invalid collector job status"
    CREATING_JOB_FOR_DISABLED_COLLECTOR = "Creating job for inactive collector"

    RUNNING_ALREADY_COMPLETE_COLLECTOR_JOB = "Running already completed job! This is not expected!"


class COLLECTOR_JOB_STATUSES:
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    INVALID = "invalid"

    ALL = [CREATED, RUNNING, COMPLETED, INVALID]
