import struct, zlib, math, os

# Utility functions for PNG

def png_chunk(tag, data):
    return (struct.pack('!I', len(data)) + tag + data +
            struct.pack('!I', zlib.crc32(tag + data) & 0xffffffff))

def save_png(path, width, height, get_pixel):
    """Save a minimal RGB PNG image.

    Args:
        path: Destination file path.
        width: Image width in pixels.
        height: Image height in pixels.
        get_pixel: Callable returning ``(r, g, b)`` for coordinates ``x, y``.
    """
    rows = []
    for y in range(height):
        row = bytearray()
        row.append(0)  # filter type 0
        for x in range(width):
            r, g, b = get_pixel(x, y)
            row.extend([r, g, b])
        rows.append(bytes(row))
    raw = b''.join(rows)
    ihdr = struct.pack('!IIBBBBB', width, height, 8, 2, 0, 0, 0)
    idat = zlib.compress(raw, 9)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(png_chunk(b'IHDR', ihdr))
        f.write(png_chunk(b'IDAT', idat))
        f.write(png_chunk(b'IEND', b''))

# Draw og-banner

def banner_pixel(x, y):
    # simple horizontal gradient
    start = (30, 64, 175)
    end = (59, 130, 246)
    t = x / 1279
    r = int(start[0] + (end[0] - start[0]) * t)
    g = int(start[1] + (end[1] - start[1]) * t)
    b = int(start[2] + (end[2] - start[2]) * t)
    return r, g, b

# After saving base gradient, overlay simple network logo

def generate_banner(path):
    """Render the Open Graph banner to ``path``."""
    width, height = 1280, 640
    # create base image array
    pixels = [bytearray([0,0,0]*width) for _ in range(height)]
    for y in range(height):
        t = y  # vertical component not used
        for x in range(width):
            r,g,b = banner_pixel(x,y)
            idx = x*3
            pixels[y][idx:idx+3] = bytes([r,g,b])
    # draw logo: three nodes connected
    def set_pixel(x,y,r,g,b):
        if 0 <= x < width and 0 <= y < height:
            idx = x*3
            pixels[y][idx:idx+3] = bytes([r,g,b])
    def draw_circle(cx,cy,rad,color):
        for y in range(cy-rad, cy+rad+1):
            for x in range(cx-rad, cx+rad+1):
                if (x-cx)**2 + (y-cy)**2 <= rad*rad:
                    set_pixel(x,y,*color)
    def draw_line(x0,y0,x1,y1,th,color):
        dx=x1-x0; dy=y1-y0
        length=int(math.hypot(dx,dy))
        for i in range(length+1):
            t=i/length
            x=int(x0+dx*t)
            y=int(y0+dy*t)
            for yy in range(y-th//2, y+th//2+1):
                for xx in range(x-th//2, x+th//2+1):
                    set_pixel(xx,yy,*color)
    # positions
    nodes=[(540,320),(640,250),(740,320)]
    # lines
    draw_line(*nodes[0],*nodes[1],12,(255,255,255))
    draw_line(*nodes[1],*nodes[2],12,(255,255,255))
    draw_line(*nodes[0],*nodes[2],12,(255,255,255))
    for cx,cy in nodes:
        draw_circle(cx,cy,40,(255,255,255))
    # write image
    def get_pixel(x,y):
        idx=x*3
        row=pixels[y]
        return row[idx],row[idx+1],row[idx+2]
    save_png(path,width,height,get_pixel)

# Minimal font for GIF
FONT = {
    'A':[
        '010',
        '101',
        '111',
        '101',
        '101',
    ],
    'C':[
        '011',
        '100',
        '100',
        '100',
        '011',
    ],
    'D':[
        '110',
        '101',
        '101',
        '101',
        '110',
    ],
    'E':[
        '111',
        '100',
        '110',
        '100',
        '111',
    ],
    'G':[
        '011',
        '100',
        '101',
        '101',
        '011',
    ],
    'I':[
        '111',
        '010',
        '010',
        '010',
        '111',
    ],
    'L':[
        '100',
        '100',
        '100',
        '100',
        '111',
    ],
    'M':[
        '101',
        '111',
        '101',
        '101',
        '101',
    ],
    'N':[
        '101',
        '111',
        '111',
        '111',
        '101',
    ],
    'O':[
        '010',
        '101',
        '101',
        '101',
        '010',
    ],
    'P':[
        '110',
        '101',
        '110',
        '100',
        '100',
    ],
    'R':[
        '110',
        '101',
        '110',
        '101',
        '101',
    ],
    'U':[
        '101',
        '101',
        '101',
        '101',
        '111',
    ],
    ' ': [
        '000',
        '000',
        '000',
        '000',
        '000',
    ],
}

FONT['T'] = [
    '111',
    '010',
    '010',
    '010',
    '010',
]
FONT['V'] = [
    '101',
    '101',
    '101',
    '101',
    '010',
]

# draw text using font

def render_text(text, scale=4, padding=2):
    """Convert text into a 1-bit pixel matrix using ``FONT``.

    Args:
        text: Message to render (supports ``\n`` for multiple lines).
        scale: Pixel scaling factor.
        padding: Padding around the rendered text.

    Returns:
        List of lists representing the monochrome image (0=black, 1=white).
    """
    lines = text.split('\n')
    width = max(len(line) for line in lines)*(3+1)*scale + padding*2
    height = len(lines)*5*scale + padding*2
    canvas = [[1]*width for _ in range(height)]  # 1=white, 0=black
    for li, line in enumerate(lines):
        y0 = padding + li*5*scale
        x0 = padding
        for ch in line:
            glyph = FONT.get(ch.upper(), FONT[' '])
            for gy,row in enumerate(glyph):
                for gx,val in enumerate(row):
                    if val=='1':
                        for ys in range(scale):
                            for xs in range(scale):
                                canvas[y0+gy*scale+ys][x0+gx*scale+xs] = 0
            x0 += (3+1)*scale
    return canvas

# LZW encoding

def lzw_compress(data, min_code_size):
    clear = 1 << min_code_size
    end = clear + 1
    dict_size = end + 1
    dictionary = {bytes([i]): i for i in range(clear)}
    w = b''
    result = [clear]
    for k in data:
        kbytes = bytes([k])
        wk = w + kbytes
        if wk in dictionary:
            w = wk
        else:
            result.append(dictionary[w])
            dictionary[wk] = dict_size
            dict_size += 1
            w = kbytes
            if dict_size >= 4095:
                result.append(clear)
                dictionary = {bytes([i]): i for i in range(clear)}
                dict_size = end + 1
    if w:
        result.append(dictionary[w])
    result.append(end)
    # pack bits
    size = min_code_size + 1
    data_out = []
    cur = 0
    bits = 0
    for code in result:
        cur |= code << bits
        bits += size
        while bits >= 8:
            data_out.append(cur & 0xFF)
            cur >>= 8
            bits -= 8
        if dict_size == (1 << size) and size < 12:
            size += 1
    if bits:
        data_out.append(cur)
    return bytes(data_out)


def gif_frame(pixels, delay):
    """Encode a single GIF frame.

    Args:
        pixels: 2D list of palette indices.
        delay: Frame delay in hundredths of a second.

    Returns:
        Bytes representing the encoded frame.
    """
    height = len(pixels)
    width = len(pixels[0])
    flat = bytes([p for row in pixels for p in row])
    min_code_size = 2
    compressed = lzw_compress(flat, min_code_size)
    def subblocks(data):
        out = bytearray()
        for i in range(0,len(data),255):
            chunk = data[i:i+255]
            out.append(len(chunk))
            out.extend(chunk)
        out.append(0)
        return bytes(out)
    frame = bytearray()
    frame.extend(b'\x21\xF9\x04\x08')
    frame.extend(struct.pack('<H', delay))
    frame.append(0)
    frame.append(0)
    frame.extend(b'\x2C')
    frame.extend(struct.pack('<HHHH',0,0,width,height))
    frame.append(0)
    frame.append(min_code_size)
    frame.extend(subblocks(compressed))
    return bytes(frame)


def save_gif(path, frames, delay):
    """Save GIF animation from frames.

    Args:
        path: Destination file path.
        frames: Sequence of pixel matrices.
        delay: Frame delay in hundredths of a second.
    """
    height = len(frames[0])
    width = len(frames[0][0])
    with open(path,'wb') as f:
        f.write(b'GIF89a')
        f.write(struct.pack('<HH', width, height))
        f.write(b'\x80\x00\x00')
        f.write(b'\xff\xff\xff\x00\x00\x00')
        f.write(b'\x21\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00')
        for pixels in frames:
            f.write(gif_frame(pixels, delay))
        f.write(b';')


def generate_gifs(out_dir):
    """Generate demonstration GIFs into ``out_dir``.

    Args:
        out_dir: Directory path where GIF files will be written.
    """
    api_frames = [
        render_text('API DEMO'),
        render_text('CALLING'),
        render_text('DONE'),
    ]
    cli_frames = [
        render_text('CLI DEMO'),
        render_text('RUN CMD'),
        render_text('DONE'),
    ]
    # delay 40 * 3 =120? actual delay in hundredths of a second
    save_gif(os.path.join(out_dir, 'api-demo.gif'), api_frames, 400)  # 4s each -> 12s
    save_gif(os.path.join(out_dir, 'cli-demo.gif'), cli_frames, 400)

if __name__ == '__main__':
    os.makedirs('assets', exist_ok=True)
    os.makedirs('media', exist_ok=True)
    generate_banner('assets/og-banner.png')
    generate_gifs('media')
