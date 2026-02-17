from PIL import Image, ImageDraw

img = Image.open('xiaohongshu-down50.png')
draw = ImageDraw.Draw(img)

click_x, click_y = 1600, 545

# 红色圆圈
radius = 15
draw.ellipse(
    [click_x - radius, click_y - radius, 
     click_x + radius, click_y + radius],
    outline='red', width=4
)

# 文字
draw.text((click_x - 60, click_y - 35), f'点击 ({click_x}, {click_y})', fill='red')

img.save('xiaohongshu-down50-marked.png')
print(f'✅ 标记完成: ({click_x}, {click_y})')
