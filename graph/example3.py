from pprint import pprint as pp

from graph import GraphTree
g = GraphTree()


g.connect(
    'head',
    'neck',
    'shoulders',
    'torso',
    'legs',
    'feet',
    'toes',
    )

g.connect('head', 'face', 'eyes')
g.connect('head', 'ears')
g.connect('head', 'hair')

g.connect('face', 'nose')
g.connect('nose', 'nostrils', 'holes')
g.connect('face', 'mouth', 'lips')

g.connect('torso', 'arms', 'hands', 'fingers', 'fingernails')
g.connect('hands', 'thumbs', 'thumbnails')

# g.splice('arms', 'elbows', 'forearms', 'wrists', 'hands')

f = g.find('neck')

g.drain()
#f.view()
pp(f.chains())

"""
(('neck', 'shoulders', 'torso', 'legs', 'feet', 'toes'),
 ('neck', 'shoulders', 'torso', 'arms', 'hands', 'fingers', 'fingernails'),
 ('neck', 'shoulders', 'torso', 'arms', 'hands', 'thumbs', 'thumbnails'))

>>> g.splice('arms', 'elbows', 'forearms', 'wrists', 'hands')

(('neck', 'shoulders', 'torso', 'legs', 'feet', 'toes'),
 ('neck',
  'shoulders',
  'torso',
  'arms',
  'elbows',
  'forearms',
  'wrists',
  'hands',
  'fingers',
  'fingernails'),
 ('neck',
  'shoulders',
  'torso',
  'arms',
  'elbows',
  'forearms',
  'wrists',
  'hands',
  'thumbs',
  'thumbnails'))
"""
