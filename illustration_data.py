# SPDX-License-Identifier: MIT
"""Shared viewports into the original 1536 × 1024 illustration sheets."""

ART = {
    'craft': ('menu-scenes.png', (18, 15, 750, 474)),
    'cocktails': ('menu-scenes.png', (786, 15, 1518, 474)),
    'mixedtea': ('menu-scenes.png', (18, 499, 750, 1001)),
    'cafemenu': ('menu-scenes.png', (786, 499, 1518, 1001)),
    'senses': ('process-scenes.png', (20, 18, 756, 497)),
    'origins': ('process-scenes.png', (781, 18, 1516, 497)),
    'rice': ('process-scenes.png', (20, 515, 756, 1001)),
    'barrels': ('process-scenes.png', (781, 515, 1516, 1001)),
}

FRONT_ART = {
    'cover': ('illustrations.png', (22, 17, 751, 497)),
    'wine': ('illustrations.png', (786, 16, 1515, 497)),
    'tea': ('illustrations.png', (22, 521, 751, 1003)),
    'coffee': ('illustrations.png', (787, 521, 1515, 1003)),
}

ART_LABELS = {
    'cover': '酒、茶与咖啡的杯中世界',
    'wine': '酒的世界',
    'tea': '茶的世界',
    'coffee': '咖啡的世界',
    'craft': '精酿啤酒的阅读情境',
    'cocktails': '鸡尾酒调配的阅读情境',
    'mixedtea': '调茶的阅读情境',
    'cafemenu': '咖啡菜单的阅读情境',
    'senses': '观察饮品风味的阅读情境',
    'origins': '探索饮品起源的阅读情境',
    'rice': '米酒酿造的阅读情境',
    'barrels': '木桶与酒杯的熟成情境',
}

LEAF_PANELS = {
    'fresh': ('tea-fresh-details.png', (0, 0, 1536, 1024), '原叶与质感观察'),
    'green': ('tea-dry-wet-details.png', (14, 14, 756, 330), '绿茶'),
    'white': ('tea-dry-wet-details.png', (780, 14, 1521, 330), '白茶'),
    'yellow': ('tea-dry-wet-details.png', (14, 352, 756, 658), '黄茶'),
    'oolong': ('tea-dry-wet-details.png', (780, 352, 1521, 658), '乌龙'),
    'black': ('tea-dry-wet-details.png', (14, 680, 756, 1009), '红茶'),
    'dark': ('tea-dry-wet-details.png', (780, 680, 1521, 1009), '黑茶实例：普洱熟茶'),
}
