# Student Result Portal

A full-stack web application for managing and viewing student results, built with Flask and modern DevOps practices.

## Features

- **Dual User Roles**: Admin and Student portals
- **Secure Authentication**: Flask-Login based authentication system
- **CSV Upload**: Admin can upload student results via CSV files
- **Responsive Design**: Tailwind CSS for modern, mobile-friendly UI
- **Database Agnostic**: Supports SQLite (development) and PostgreSQL (production)
- **Containerized**: Docker and Docker Compose for easy deployment
- **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions
- **Infrastructure as Code**: Terraform for AWS infrastructure
- **Configuration Management**: Ansible for server provisioning

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL (for production)
- Docker & Docker Compose (optional)

### Local Development (Without Docker)

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/student-result-portal.git
   cd student-result-portal