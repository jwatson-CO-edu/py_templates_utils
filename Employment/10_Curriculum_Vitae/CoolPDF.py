# sudo apt install libcairo2-dev
# python3.11 -m pip install pycairo --user

import cairo

def create_resume(filename="resume.pdf"):
    width, height = 600, 800  # Set PDF dimensions
    surface = cairo.PDFSurface(filename, width, height)
    context = cairo.Context(surface)
    
    # Draw quadrants
    context.set_line_width(2)
    context.move_to(width / 2, 0)
    context.line_to(width / 2, height)
    context.move_to(0, height / 2)
    context.line_to(width, height / 2)
    context.stroke()
    
    # Draw central circle
    circle_x, circle_y, circle_radius = width / 2, height / 2, 80
    context.arc(circle_x, circle_y, circle_radius, 0, 2 * 3.1416)
    context.set_source_rgb(0.2, 0.2, 0.8)  # Set circle color
    context.fill_preserve()
    context.set_source_rgb(0, 0, 0)
    context.stroke()
    
    # Add text to central circle
    context.set_source_rgb(1, 1, 1)
    context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    context.set_font_size(14)
    
    def draw_text(text, x, y, size=14, color=(0, 0, 0)):
        context.set_source_rgb(*color)
        context.set_font_size(size)
        context.move_to(x, y)
        context.show_text(text)
    
    draw_text("John Doe", circle_x - 35, circle_y - 10, 14, (1, 1, 1))
    draw_text("johndoe@example.com", circle_x - 50, circle_y + 10, 10, (1, 1, 1))
    draw_text("(123) 456-7890", circle_x - 40, circle_y + 25, 10, (1, 1, 1))
    
    # Add section titles
    draw_text("BIOGRAPHICAL DATA", 20, 30, 12)
    draw_text("SKILLS", width - 120, 30, 12)
    draw_text("EXPERIENCE", 20, height / 2 + 30, 12)
    draw_text("EDUCATION", width - 120, height / 2 + 30, 12)
    
    # Add sample content
    draw_text("Age: 30", 20, 50, 10)
    draw_text("Python, C++, Java", width - 120, 50, 10)
    draw_text("Software Engineer at XYZ", 20, height / 2 + 50, 10)
    draw_text("B.S. in Computer Science", width - 120, height / 2 + 50, 10)
    
    # Save the PDF
    surface.finish()
    print(f"Resume saved as {filename}")

create_resume()
