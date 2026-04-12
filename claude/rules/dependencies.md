# Dependencies

## Before adding a dependency

- **Check if existing packages already cover the need.** Don't add `lodash` for one utility function you can write in 5 lines.
- Evaluate: maintenance status (last commit, open issues), weekly downloads, license compatibility, bundle size (frontend), transitive dependency count.
- Prefer well-maintained, widely-adopted libraries over obscure ones. A library with 10 GitHub stars and no recent commits is a liability.
- Check for known vulnerabilities before installing.

## Version management

- **Pin exact versions** in production dependencies. Use `package-lock.json` / `uv.lock` / `requirements.txt` with hashes.
- Commit lockfiles. Always. The lockfile is how you ensure reproducible builds.
- Update dependencies deliberately, not blindly. Review changelogs before bumping major versions.
- Run `npm audit` / `pip audit` regularly. Don't ship code with known high/critical vulnerabilities.

## Removal

- When removing a dependency, verify nothing imports it. Check transitive usage — other packages may depend on it.
- Clean up configuration files, types, and utility wrappers associated with the removed dependency.

## Frontend-specific

- Be conscious of bundle size. Tree-shakeable > monolithic. Importing one function from a 500KB library is not acceptable if a 2KB alternative exists.
- Prefer native browser APIs over polyfill libraries when browser support allows.
- Don't add UI component libraries for one component. Build it or use headless primitives.

## Backend-specific

- Prefer async-compatible libraries in async codebases. A synchronous HTTP client in an async FastAPI app defeats the purpose.
- Pin Python dependencies with `pip freeze` or `uv lock`. Don't use loose version ranges in production.
