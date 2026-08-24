# M.I. ENGINEERING WORKS

Official website and business management platform for **M.I. Engineering Works**, built with Django.

The platform is designed to provide product information, media and document management, customer accounts, enquiries, real-time business communication, quotations, invoices, and staff management through a centralized system.

---

## Features

### Website & Product Management

* Product catalogue
* Product categories
* Materials, grades, standards, and sizes
* Product specifications
* Multiple product images
* Product publishing and management
* Search and filtering
* SEO-friendly product pages

### Content Management

Admin-managed content for:

* Blog posts
* Gallery images
* Certificates
* Catalogues
* PDF documents
* Videos
* Other business media

Content can be created, updated, published, unpublished, replaced, or removed through the administration system.

### Customer Accounts

Customers can:

* Sign up
* Log in
* Manage their profile
* Submit product enquiries
* View previous enquiries
* Check enquiry status
* Communicate with staff
* Receive quotations and invoices
* Access enquiry-related documents

### Enquiry Management

Each customer enquiry is maintained as an individual business thread containing:

* Enquiry number
* Customer
* Product
* Quantity
* Requirements
* Status
* Assigned staff member
* Messages
* Attachments
* Quotations
* Invoices
* Conversation history

Example flow:

```text
Customer
    ↓
Product
    ↓
Submit Enquiry
    ↓
My Enquiries
    ↓
Staff Assignment
    ↓
Business Chat
    ↓
Quotation
    ↓
Invoice / Documents
    ↓
Enquiry Completion
```

### Business Chat

Enquiry-based communication system for customers and staff.

Supported communication will include:

* Text messages
* Images
* PDFs
* Excel files
* Quotations
* Invoices
* Business documents

The chat system is intended for business communication only.

Voice calls and video calls are not part of the platform.

### Staff & Permissions

The administration system will support role-based access control.

Example roles:

* Super Admin
* Sales Staff
* Content Staff

Permissions can control access to areas such as:

* Products
* Customers
* Enquiries
* Messages
* Quotations
* Documents
* Gallery
* Certificates
* Blogs
* Staff management

---

## Technology Stack

| Component                 | Technology            |
| ------------------------- | --------------------- |
| Backend                   | Django                |
| Language                  | Python                |
| Database                  | PostgreSQL            |
| Package Manager           | uv                    |
| Templates                 | Django Templates      |
| Styling                   | Tailwind CSS          |
| Dynamic UI                | HTMX                  |
| Lightweight JavaScript    | Alpine.js             |
| Images                    | Pillow                |
| Environment Configuration | django-environ        |
| Real-time Communication   | Django Channels       |
| Channel Layer / Cache     | Redis                 |
| Background Tasks          | Celery                |
| File Storage              | S3-compatible storage |
| Excel Documents           | openpyxl              |
| PDF Documents             | ReportLab             |

Some dependencies will be introduced as their corresponding features are implemented.

---

## Project Structure

```text
mi_engineering/
│
├── mi_engineering/
│   ├── __init__.py
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   │
│   └── settings/
│       ├── __init__.py
│       ├── base.py
│       ├── dev.py
│       └── prod.py
│
├── core/
├── accounts/
├── business/
│
├── templates/
├── static/
├── media/
│
├── .example.env
├── .gitignore
├── .python-version
├── manage.py
├── pyproject.toml
├── uv.lock
└── README.md
```

### Django Applications

#### `core`

Handles the public website and content-related functionality.

Planned responsibilities include:

* Homepage
* Products
* Categories
* Materials
* Grades
* Standards
* Product specifications
* Gallery
* Certificates
* Catalogues
* Videos
* Blog posts

#### `accounts`

Handles authentication, customers, staff, and permissions.

Planned responsibilities include:

* Custom user model
* Customer accounts
* Customer profiles
* Staff accounts
* Authentication
* Email verification
* Password management
* Roles
* Permissions

#### `business`

Handles customer-to-company business interactions.

Planned responsibilities include:

* Enquiries
* Enquiry statuses
* Staff assignments
* Business chat
* Chat attachments
* Quotations
* Invoices
* Business documents
* Notifications

---

## Development Setup

### Requirements

Make sure the following are installed:

* Python
* uv
* Git

PostgreSQL will also be required when using the production database configuration.

### Clone the Repository

```bash
git clone <repository-url>
cd mi_engineering
```

### Install Dependencies

Dependencies are managed using **uv**.

```bash
uv sync
```

The Python version used by the project is defined in:

```text
.python-version
```

### Environment Configuration

Copy the example environment file:

```bash
cp .example.env .env
```

Update the values inside `.env` for your environment.

Example:

```dotenv
SECRET_KEY=your-secret-key

ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=mi_engineering
DB_USER=mi_engineering
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=5432

EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@example.com
EMAIL_HOST_PASSWORD=your-email-password

DEFAULT_FROM_EMAIL=M.I. Engineering Works <noreply@example.com>
```

> Never commit the actual `.env` file to Git.

---

## Django Settings

Settings are separated by environment.

```text
mi_engineering/settings/
├── __init__.py
├── base.py
├── dev.py
└── prod.py
```

### `base.py`

Contains settings shared between all environments.

### `dev.py`

Contains development-specific configuration such as:

* `DEBUG = True`
* Local hosts
* Development database
* Console email backend

### `prod.py`

Contains production-specific configuration such as:

* `DEBUG = False`
* PostgreSQL
* HTTPS security
* Secure cookies
* Production email configuration

---

## Running the Development Server

Run Django using uv:

```bash
uv run python manage.py runserver
```

The development server will normally be available at:

```text
http://127.0.0.1:8000/
```

---

## Django Commands

Check the project configuration:

```bash
uv run python manage.py check
```

Create migrations:

```bash
uv run python manage.py makemigrations
```

Apply migrations:

```bash
uv run python manage.py migrate
```

Create an administrator:

```bash
uv run python manage.py createsuperuser
```

Start the development server:

```bash
uv run python manage.py runserver
```

Open the Django administration interface at:

```text
http://127.0.0.1:8000/admin/
```

---

## Adding Dependencies

Use `uv add` instead of manually editing dependency files.

Example:

```bash
uv add pillow
```

Development dependency:

```bash
uv add --dev pytest
```

Remove a dependency:

```bash
uv remove package-name
```

Synchronize the environment:

```bash
uv sync
```

Both of these files should be committed:

```text
pyproject.toml
uv.lock
```

---

## Planned Development

The project will be developed incrementally.

### Foundation

* [ ] Django project configuration
* [ ] Development/production settings
* [ ] Environment configuration
* [ ] PostgreSQL configuration
* [ ] Base templates and static files

### Accounts

* [ ] Custom user model
* [ ] Email-based authentication
* [ ] Customer registration
* [ ] Login/logout
* [ ] Password reset
* [ ] Customer profiles
* [ ] Staff accounts
* [ ] Roles and permissions

### Products & Content

* [ ] Product categories
* [ ] Products
* [ ] Materials
* [ ] Grades
* [ ] Standards
* [ ] Specifications
* [ ] Product images
* [ ] Gallery
* [ ] Certificates
* [ ] Catalogues
* [ ] Videos
* [ ] Blog

### Enquiries

* [ ] Product enquiry form
* [ ] Unique enquiry numbers
* [ ] My Enquiries
* [ ] Enquiry status
* [ ] Staff assignment
* [ ] Enquiry history

### Business Chat

* [ ] Enquiry-based conversations
* [ ] Real-time messaging
* [ ] Message history
* [ ] Image attachments
* [ ] PDF attachments
* [ ] Excel/document attachments
* [ ] Unread messages

### Documents

* [ ] Quotations
* [ ] Invoices
* [ ] PDF generation
* [ ] Excel generation
* [ ] Private customer documents
* [ ] Document download permissions

### Administration

* [ ] Dashboard
* [ ] Product management
* [ ] Content management
* [ ] Customer management
* [ ] Enquiry management
* [ ] Chat interface
* [ ] Staff management
* [ ] Role-based permissions
* [ ] Notifications
* [ ] Audit logs

### Production

* [ ] PostgreSQL
* [ ] Redis
* [ ] Background workers
* [ ] Object storage
* [ ] HTTPS
* [ ] Production email
* [ ] Logging
* [ ] Backups
* [ ] Deployment configuration

---

## Security

The application should follow standard Django production security practices.

Important requirements include:

* Secrets stored in environment variables
* `DEBUG` disabled in production
* HTTPS enforced in production
* Secure session cookies
* Secure CSRF cookies
* Password validation
* Permission checks on customer documents
* Role-based staff authorization
* File type and size validation
* Private storage for quotations and invoices
* Audit logging for important staff actions

Customer enquiries, quotations, invoices, and private documents must never be exposed as unrestricted public files.

---

## License

This project is proprietary software developed for **M.I. ENGINEERING WORKS**.

Unauthorized copying, distribution, modification, or commercial use of this project is prohibited unless explicitly authorized by the project owner.
