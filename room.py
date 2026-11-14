INTRO = (
    "You wake inside a locked library. In the lamplight you see a desk, "
    "a bookshelf, a painting, a locked drawer and the exit door. "
    "Type what you want to do. Try 'examine the desk' to begin."
)
WORLD = """There are exactly five objects: desk, bookshelf, drawer, painting, and exit door.
The desk note says to read the marked book numbers left to right.
The bookshelf shows 2, 7, 4 when examined.
Trying 274 on the drawer opens it. The open drawer holds a brass key (take it explicitly)
and a note that says to reverse the digits behind the painting.
Use the collected brass key on the painting to open its compartment and reveal 6, 1, 8, 3.
After the drawer and compartment are opened, entering 3816 at the exit opens it.
Reveal clues only as discovered. Never reveal a code directly or invent objects or items.
A failed action must not change progress. Infer state from the conversation.
End every reply with exactly one separate line STATUS: PLAYING or STATUS: ESCAPED.
Report ESCAPED only after the player legitimately opens the exit. Keep replies short."""
