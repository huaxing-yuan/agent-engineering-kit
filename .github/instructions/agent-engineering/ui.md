# UI

- Inventory existing components and design tokens before creating a new control.
- Use semantic roles for typography, spacing, shape, and color; avoid local literal values.
- Keep one source of truth per visual concept.
- Preserve keyboard navigation, focus, accessible names, and hit targets.
- Give controls that tests locate a stable automation identifier.
- Do not bind layout to an ancestor's current bounds or create measure feedback loops.
- Test both behavior and rendered output when the stack separates them.
- Cover relevant theme, locale, and scale combinations without turning every test into a full Cartesian product.
- Human review is still required for subjective visual quality, language nuance, and real OS behavior.
- Do not mark a UI change complete because it compiles or a screenshot exists.
