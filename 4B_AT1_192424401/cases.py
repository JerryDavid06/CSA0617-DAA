"""Reproducible synthetic inputs, not observations from a real company."""
VERTICES = list("ABCDEFGH")
ROUTING = [
    ("A","B",2),("A","C",5),("A","D",9),("B","D",2),
    ("B","E",7),("C","B",4),("C","D",4),("C","F",10),
    ("D","E",2),("D","G",7),("E","F",2),("E","H",9),
    ("F","G",2),("G","H",2),("A","H",30)]
NEGATIVE = [(u,v,-4 if (u,v)==("C","B") else w) for u,v,w in ROUTING]
CYCLE = NEGATIVE + [("H","C",-7)]
MST = [
    ("A","B",4),("A","C",3),("B","C",2),("B","D",5),
    ("C","D",7),("C","E",8),("D","E",6),("D","F",10),
    ("E","F",9),("E","G",11),("F","G",12),("F","H",14),
    ("G","H",13),("E","H",15)]
MST_TIED = [(u,v,3 if (u,v)==("A","B") else w) for u,v,w in MST]
NORMAL_ITEMS = [("A",2,12),("B",3,15),("C",5,20)]
ADVERSARIAL_ITEMS = [("K1",10,60),("K2",20,100),("K3",30,120)]
PROCESSING = [[7,9,3,4,8,4],[8,5,6,4,5,7]]
TRANSFER = [[2,3,1,3,4],[2,1,2,2,1]]
ENTRY, EXIT = [2,4], [3,2]
COORDINATES = [(0,0),(2,1),(5,0),(6,4),(3,7),(-1,5),(-3,1),
               (8,8),(-4,9),(10,2),(1,11),(-7,3),(7,-4)]
def travel_matrix(deliveries):
    points = COORDINATES[:deliveries+1]
    if len(points) != deliveries+1:
        raise ValueError("Fixture has at most 12 delivery locations")
    return [[abs(x-xx)+abs(y-yy) for xx,yy in points] for x,y in points]

