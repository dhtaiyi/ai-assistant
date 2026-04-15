from PIL import Image, ImageDraw

# 打开截图
img = Image.open('xiaohongshu-raw.png')
draw = ImageDraw.Draw(img)

# 点击位置
click_x, click_y = 1600, 495

# 绘制点击标记 (红色圆圈)
radius = 15
draw.ellipse(
    [click_x - radius, click_y - radius, 
     click_x + radius, click_y + radius],
    outline='red', width=4
)

# 添加文字
draw.text((click_x - 60, click_y - 35), f'点击位置 ({click_x}, {click_y})', fill='red')

# 保存
img.save('xiaohongshu-with-click.png')
print(f'✅ 已标记点击位置: ({click_x}, {click_y})')
