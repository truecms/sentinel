# Product Requirements Document (PRD)

## Elevator Pitch
This platform is a centralized monitoring and reporting solution designed to track and measure the application of security patches and module updates across multiple Drupal websites. By aggregating data pushed from each website, it enables agencies and site owners to quickly identify outstanding security patches, assess compliance with service level agreements (SLAs), and review historical performance trends—all through an intuitive, dashboard-driven interface.

## Who is this App For?
- **Agencies:** Firms managing groups of websites who need a single dashboard to monitor security patch compliance and overall module update efficiency.
- **Site Owners:** Website administrators who want to quickly view the status of their installed Drupal modules, check for outdated versions or pending security updates, and easily navigate to detailed module information.
- **Service Desk Managers:** Professionals responsible for generating periodic reports on module updates and SLA compliance.
- **Organizational Users:** Supported from day one with two roles: Organization Administrator and Organizational User.
- **Super Users:** Responsible for overall management and actions across all organizations and users (a dedicated dashboard for super users is planned for a future roadmap).

## Functional Requirements
- **Headless API Application:**  
  - Built with Python FastAPI, supporting asynchronous processing.
  - Database backend using PostgreSQL with SQLAlchemy, with Redis for rate limiting and buffering.
- **Data Ingestion:**  
  - Each Drupal site pushes module version and patch data to the dashboard via a custom Drupal module during cron runs.
  - Differentiation between security and non-security module updates.
- **Reporting & Dashboard Capabilities:**  
  - Real-time and historical reporting on:
    - Unapplied security patches.
    - Time taken to apply patches relative to custom SLAs.
    - Overall update performance with detailed views (daily, monthly, year-to-date).
- **Subscription & SLA Management:**  
  - **Beta Testing Phase:** During beta testing, the application will be free for everyone, offering the most granular SLA (e.g., hourly updates) with an excellent SLA performance.
  - **Future Premium Subscription:** Although premium features are free during the beta phase, future subscription models will differentiate based on update frequency—free tiers with weekly data and premium tiers with more granular data.
- **Email Notifications:**  
  - Customers can opt-in to email notifications.
  - Notification options include:
    - Immediate alerts to site owners or site admins when a new security update becomes available.
    - Monthly reports summarizing the number of security updates introduced, including statistics such as a list of modules and the time elapsed since each update became available.
  - Users will have the ability to enable or disable these notifications.
- **Security & Authentication:**  
  - API Key-based and JWT user authentication.
  - Support for two-factor authentication (2FA) and backup codes.
- **Scalability & Integration:**  
  - Designed to accommodate future enhancements like push notifications and mobile app integration (React Native).

## User Stories
1. **Service Desk Manager Reporting:**  
   - *As a service desk manager, I need to generate monthly reports that detail which Drupal modules were updated and how many security updates were applied, so that I can demonstrate compliance with client SLAs (including tight SLAs such as 12-hour patch application) over various periods (e.g., last 12 months, year-to-date).*
2. **Site Owner Dashboard:**  
   - *As a site owner, I want a dashboard to browse all installed modules on my website, filter for outdated or security-critical modules, click through to the corresponding Drupal.org module pages, and see metrics such as the number of days since an update became available. I also want the ability to set a custom SLA to compare actual performance against my expectations.*
3. **Email Notification & Alerts:**  
   - *As a customer, I want the option to receive email notifications so that I am alerted immediately when a security update is released, and also receive a monthly report summarizing update statistics, which I can enable or disable based on my preference.*

## User Interface
- **Login & Authentication Screen:**  
  - User login with support for two-factor authentication.
  - Profile management including password changes, 2FA settings, and backup codes.
- **Dashboard Views:**  
  - A suite of dashboards offering visualizations for:
    - Security patch status and compliance metrics.
    - Historical trends on patch application times.
    - Detailed module status overview with filters for security updates and update age.
- **Interactive Reports:**  
  - Ability to click through from a dashboard to detailed module information, including direct links to Drupal.org pages.
- **Responsive & Intuitive Design:**  
  - A simplistic yet effective front-end design that prioritizes ease of use for busy administrators, with clear call-to-action buttons and accessible reporting formats.
- **Organizational Roles:**  
  - Support for Organization Administrators and Organizational Users from day one.
  - A future roadmap includes adding a dedicated dashboard for Super Users to manage activities across organizations.