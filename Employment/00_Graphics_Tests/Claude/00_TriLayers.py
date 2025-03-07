# Source: https://claude.site/artifacts/c954686e-c5d2-4c69-8b61-c53e8ab336fd

import random
import math
import svgwrite
import cairosvg
import argparse

def generate_random_triangle(width, height, min_size=30, max_size=100, stroke_width=3):
    """Generate a random triangle within the canvas dimensions."""
    # Random center point
    center_x = random.uniform(0, width)
    center_y = random.uniform(0, height)
    
    # Random size
    size = random.uniform(min_size, max_size)
    
    # Random rotation angle
    angle = random.uniform(0, 2 * math.pi)
    
    # Generate three points around the center
    points = []
    for i in range(3):
        # Create points at 120 degrees apart
        point_angle = angle + (i * 2 * math.pi / 3)
        point_x = center_x + size * math.cos(point_angle)
        point_y = center_y + size * math.sin(point_angle)
        points.append((point_x, point_y))
    
    return {
        "points": points,
        "stroke_width": stroke_width
    }

def create_multi_layer_svg(width, height, num_layers=5, triangles_per_layer=10):
    """Create a multi-layer SVG with random triangles."""
    # Create SVG document
    dwg = svgwrite.Drawing(size=(width, height))
    
    # Add a white background
    dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill='white'))
    
    # Create layers with increasing opacity
    for layer in range(num_layers):
        # Calculate opacity for this layer (0 to 1)
        opacity = layer / (num_layers - 1) if num_layers > 1 else 1
        
        # Create a group for this layer
        group = dwg.g(opacity=opacity)
        
        # Add random triangles to this layer
        for _ in range(triangles_per_layer):
            triangle = generate_random_triangle(width, height)
            polygon = dwg.polygon(points=triangle["points"],
                                 stroke='black',
                                 stroke_width=triangle["stroke_width"],
                                 fill='none')
            group.add(polygon)
        
        # Add the group to the drawing
        dwg.add(group)
    
    return dwg

def save_output(drawing, filename, output_format='svg'):
    """Save the drawing in the specified format (svg or pdf)."""
    base_filename = filename.split('.')[0] if '.' in filename else filename
    
    # Save as SVG
    svg_filename = f"{base_filename}.svg"
    drawing.saveas(svg_filename)
    print(f"SVG saved to {svg_filename}")
    
    # If PDF format is requested, convert SVG to PDF
    if output_format.lower() == 'pdf':
        pdf_filename = f"{base_filename}.pdf"
        svg_content = drawing.tostring()
        cairosvg.svg2pdf(bytestring=svg_content, write_to=pdf_filename)
        print(f"PDF saved to {pdf_filename}")
    
    return svg_filename

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Generate a multi-layer SVG with random triangles')
    parser.add_argument('--width', type=int, default=800, help='Width of the canvas')
    parser.add_argument('--height', type=int, default=600, help='Height of the canvas')
    parser.add_argument('--layers', type=int, default=7, help='Number of layers')
    parser.add_argument('--triangles', type=int, default=12, help='Triangles per layer')
    parser.add_argument('--min-size', type=int, default=30, help='Minimum triangle size')
    parser.add_argument('--max-size', type=int, default=100, help='Maximum triangle size')
    parser.add_argument('--stroke-width', type=int, default=3, help='Stroke width for triangles')
    parser.add_argument('--output', type=str, default='random_triangles', help='Output filename (without extension)')
    parser.add_argument('--format', type=str, choices=['svg', 'pdf', 'both'], default='svg', 
                        help='Output format: svg, pdf, or both')
    
    args = parser.parse_args()
    
    # Generate the SVG
    svg_drawing = create_multi_layer_svg(
        width=args.width,
        height=args.height,
        num_layers=args.layers,
        triangles_per_layer=args.triangles
    )
    
    # Save in requested format(s)
    if args.format == 'both':
        save_output(svg_drawing, args.output, 'svg')
        save_output(svg_drawing, args.output, 'pdf')
    else:
        save_output(svg_drawing, args.output, args.format)

if __name__ == "__main__":
    main()