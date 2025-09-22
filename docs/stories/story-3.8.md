# Story 3.8: PyPI & Docker Hub Publishing

## Status
Draft

## Story
**As a** developer,
**I want** Ordo on PyPI and Docker Hub,
**so that** I can install and run it easily.

## Acceptance Criteria
1. A GitHub Actions workflow is created to build and publish the application to PyPI.
2. The workflow is triggered on new version tags (e.g., `v1.0.0`).
3. The GitHub Actions workflow also builds and pushes a Docker image to Docker Hub.
4. The Docker image is tagged with the version and `latest`.

## Tasks / Subtasks
- [ ] Create a `publish.yml` workflow for GitHub Actions.
- [ ] Configure the `pyproject.toml` file for PyPI packaging.
- [ ] Add secrets to the GitHub repository for PyPI and Docker Hub credentials.
- [ ] Test the publishing process.

## Dev Notes
- **Adoption:** This is a key requirement for making the project easy to adopt (NFR17).

### Testing
- The workflow needs to be tested in a staging or pre-release environment before being used for a production release.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial draft | Sarah (PO) |
