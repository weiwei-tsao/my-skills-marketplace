# <TICKET-ID> PR Notes

## PR title

```text
fix(<TICKET-ID>): short description
```

## PR description

```md
## Summary
- 

## Test
- 

## Notes
- 
```

## Commit

Handled by the `git-commit` skill when `/ticket-finish` runs (or
`conventions.md`'s "Commit / PR title style" if that skill isn't
installed). Never committed without the user confirming the exact message
first.

## Status update — ready for verification

```text
Ready for verification on <env>. Tested <area>, confirmed <result>.
```

## Status update — fixed and verified

```text
Fixed and verified on <env>. No longer seeing <issue> on <surface>.
```

## Status update — deployed

```text
Deployed to production. Please flag if anything looks off.
```

## Reviewer notes

- 
