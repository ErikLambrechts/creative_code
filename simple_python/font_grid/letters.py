# Initialize SVG canvas for uppercase
dwg_upper = svgwrite.Drawing('alphabet_uppercase.svg', profile='tiny', size=(A3_WIDTH * mm, A3_HEIGHT * mm))

# Uppercase alphabet letters
uppercase_alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

# Draw grid with uppercase letters and patterns
for row in range(GRID_ROWS):
    for col in range(GRID_COLS):
        letter_index = row * GRID_COLS + col
        if letter_index >= len(uppercase_alphabet):
            break
        letter = uppercase_alphabet[letter_index]
        x = col * CELL_WIDTH + BOLT_PADDING
        y = row * CELL_HEIGHT + BOLT_PADDING

        # Draw the arrow-rounded bolt shape (rounded rectangle)
        dwg_upper.add(dwg_upper.rect(insert=(x, y), size=(CELL_WIDTH - 2 * BOLT_PADDING, CELL_HEIGHT - 2 * BOLT_PADDING),
                                     rx=10, ry=10, stroke='black', fill='none', stroke_width=2))

        # Draw the letter with the corresponding pattern
        text_x = x + (CELL_WIDTH - 2 * BOLT_PADDING) / 2
        text_y = y + (CELL_HEIGHT - 2 * BOLT_PADDING) / 2 + FONT_SIZE / 3
        letter_text = dwg_upper.text(letter, insert=(text_x, text_y), font_size=FONT_SIZE, font_family="Arial",
                                     text_anchor="middle", alignment_baseline="middle", fill="none", stroke="black", stroke_width=1)
        letter_text['fill'] = get_pattern(letter_index)
        dwg_upper.add(letter_text)

# Save the uppercase drawing
dwg_upper.save()
print("SVG file 'alphabet_uppercase.svg' created.")
