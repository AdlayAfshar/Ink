# Development Workflow

## GitHub Issues

Use GitHub Issues to describe each unit of work. Issues should include the problem, acceptance criteria, and technical notes.

## GitHub Projects Kanban

Use a GitHub Projects board to plan work across columns such as Backlog, Ready, In Progress, Review, and Done.

## Pull Requests

Every meaningful change should go through a pull request. Pull requests should explain what changed, how it was tested, and what learning outcome the work supported.

The `main` branch is protected. Pull requests cannot merge until the backend test workflow has completed successfully. The required GitHub status check is `test`, from the `Tests` workflow.

Merges into `main` also require at least one approving review, code owner review approval, and all conversations to be resolved. Force pushes and branch deletion are not allowed for `main`.

## Architecture Decision Records

Use Architecture Decision Records for important technical choices. ADRs should capture context, decision, and consequences so future readers can understand why the project evolved in a specific direction.

## Iterative Milestones

Prefer small milestones that produce working, reviewable increments. Each milestone should strengthen one part of the backend rather than adding broad unfinished scope.
