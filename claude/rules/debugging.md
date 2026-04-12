# Debugging

## Process

1. **Reproduce first.** If you can't reproduce the bug, you can't verify the fix. Get a reliable reproduction before touching code.
2. **Read the error.** The actual error message, stack trace, and context — not a summary of it. Error messages exist for a reason.
3. **Trace the data flow.** Start from the symptom and trace backward. Where does the bad data come from? Where does it diverge from what's expected? Follow the data through each layer.
4. **Isolate the layer.** Is this a frontend issue, backend issue, database issue, or infrastructure issue? Narrow it down before diving into code. Use network tab, server logs, database queries to pinpoint.
5. **Form a hypothesis.** Based on what you've observed, what do you think is happening? What evidence would confirm or deny it?
6. **Test the hypothesis.** Add logging, use a debugger, write a failing test. Don't just read code and guess — verify.
7. **Fix the root cause.** Not the symptom. If a null check fixes the crash but the data should never be null, find out _why_ it's null.
8. **Verify the fix.** Run the reproduction again. Run the tests. Check that you didn't break something else.
9. **Add a test.** If this bug wasn't caught by existing tests, add one that would have caught it.

## Anti-patterns

- **Don't shotgun debug.** Changing random things until the error goes away is not debugging. You'll introduce new bugs and won't understand what fixed the original one.
- **Don't blame the framework first.** It's almost always your code. Check your assumptions before filing a framework bug.
- **Don't ignore warnings.** Deprecation warnings, console warnings, linter warnings — they're telling you something. Address them before they become errors.
- **Don't add try/catch to hide the problem.** If you're catching an exception just to make the error go away, you're hiding the bug, not fixing it.

## Tools

- **Browser DevTools:** Network tab for API issues, Console for JS errors, Performance tab for rendering issues, Application tab for storage/cookies.
- **Server logs:** Check them first. Most backend bugs are immediately visible in the logs if you look.
- **Database:** Use `EXPLAIN ANALYZE` for slow queries. Check the actual data — don't assume it matches what you expect.
- **Git blame/log:** When did this behavior change? What commit introduced it? Who changed it and why?

## When you're stuck

- **Rubber duck it.** Explain the problem out loud (or in writing). The act of explaining often reveals the gap in your understanding.
- **Question your assumptions.** What are you taking for granted? Is that function actually being called? Is that variable actually what you think it is? Is the data actually in the format you expect?
- **Step back.** If you've been staring at the same code for 30 minutes, you're probably too close. Look at the bigger picture.
