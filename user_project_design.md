# User and Project Management Design

Based on the requirements from "Story 1: העלאת תמונה (Image Upload)", this document outlines the proposed database schema and basic API structure for managing users and projects, considering the need for multiple users per project with different permission levels and public projects.

## Database Schema

The design includes three main tables: `users`, `projects`, and `user_project_permissions`.

*   **`users` table:**
    *   `id`: Primary key, unique identifier for the user.
    *   `username`: Unique username for the user.
    *   `email`: User's email address (optional).
    *   `created_at`: Timestamp for when the user was created.
    *   `updated_at`: Timestamp for when the user was last updated.

*   **`projects` table:**
    *   `id`: Primary key, unique identifier for the project.
    *   `name`: Name of the project.
    *   `description`: Description of the project (optional).
    *   `is_public`: Boolean flag indicating if the project is publicly accessible (anyone can use the model).
    *   `created_at`: Timestamp for when the project was created.
    *   `updated_at`: Timestamp for when the project was last updated.

*   **`user_project_permissions` table:**
    *   `user_id`: Foreign key referencing the `id` in the `users` table.
    *   `project_id`: Foreign key referencing the `id` in the `projects` table.
    *   `permission_level`: Defines the user's role in the project (e.g., 'user_model_only', 'model_editor', 'admin').
    *   `created_at`: Timestamp for when the permission was granted.
    *   `updated_at`: Timestamp for when the permission was last updated.
    *   Composite primary key on `user_id` and `project_id` to ensure a user has only one permission entry per project.

### Database Schema Diagram

```mermaid
erDiagram
    users {
        INT id PK
        VARCHAR username UK
        VARCHAR email
        DATETIME created_at
        DATETIME updated_at
    }

    projects {
        INT id PK
        VARCHAR name
        VARCHAR description
        BOOLEAN is_public
        DATETIME created_at
        DATETIME updated_at
    }

    user_project_permissions {
        INT user_id FK
        INT project_id FK
        VARCHAR permission_level
        DATETIME created_at
        DATETIME updated_at
        PK (user_id, project_id)
    }

    users ||--o{ user_project_permissions : ""
    projects ||--o{ user_project_permissions : ""
```

## Basic API Structure

The API endpoints will handle the many-to-many relationship and permission checks.

*   **User Endpoints:**
    *   `POST /users`: Create a new user.
    *   `GET /users/{id}`: Get details of a specific user.
    *   `GET /users`: List all users (requires authentication/authorization).
    *   `GET /users/{user_id}/projects`: List all projects a user is associated with (either through `user_project_permissions` or if the project is public).

*   **Project Endpoints:**
    *   `POST /projects`: Create a new project. The creating user will be added to `user_project_permissions` with 'admin' permission.
    *   `GET /projects/{id}`: Get details of a specific project. Access is granted if the user has an entry in `user_project_permissions` for this project or if `is_public` is true.
    *   `PUT /projects/{id}`: Update project details. Requires 'admin' or 'model_editor' permission.
    *   `DELETE /projects/{id}`: Delete a project. Requires 'admin' permission.

*   **Project Permission Endpoints:**
    *   `POST /projects/{project_id}/permissions`: Add a user to a project with a specific permission level. Requires 'admin' permission on the project.
    *   `PUT /projects/{project_id}/permissions/{user_id}`: Update a user's permission level on a project. Requires 'admin' permission on the project.
    *   `DELETE /projects/{project_id}/permissions/{user_id}`: Remove a user from a project. Requires 'admin' permission on the project.