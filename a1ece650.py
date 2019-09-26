import sys
import re


def cal_distance_points_2( point1=(), point2 = ()):
    """
    calculate the distance between two points
    :param point1: (x1,y1)
    :param point2: (x2,y2)
    :return: distance * distance
    """
    d = pow((point1[0]-point2[0]),2) + pow((point1[1]-point2[1]),2)
    return d


def Create_line(estreet={}):
    """
    Create segments according to the street points
    :param estreet:input street points dictionary
    :return:estreet_seg
    """
    estreet_seg = {}
    for eachstreet in estreet:
        estreet_line = []
        for j in range(0,len(estreet[eachstreet])-1):
            estreet_line.append([estreet[eachstreet][j],estreet[eachstreet][j+1]])
        estreet_seg[eachstreet] = estreet_line
    return estreet_seg


def line_intersection(line1, line2):
    """
    calculate the intersection point coordinate
    :param line1: [(x1,y1),(x2,y2)]
    :param line2: [(x1,y2),(x1,y2)]
    :return: the intersection point coordinate(x,y) if there is an intersection, else return 0
    """

    if line1 == [] or line2 == []:
        return 0
    xdiff = (float(line1[0][0] - line1[1][0]),float(line2[0][0] - line2[1][0]))
    ydiff = (float(line1[0][1] - line1[1][1]), float(line2[0][1] - line2[1][1]))

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        return 0


    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    if PointOnSeg((x,y),line1) and PointOnSeg((x,y),line2):
        return x,y
    else:
        return 0


def PointOnSeg((x,y), line):
    """
    Judge if the point (x,y) is on the segment
    :param line:[(x1,y1),(x2,y2)]
    :return: True if it is on the segment, else return false
    """
    line_max_x = max(line[0][0],line[1][0])
    line_min_x = min(line[0][0],line[1][0])
    line_max_y = max(line[0][1],line[1][1])
    line_min_y = min(line[0][1],line[1][1])
    if line_min_x<=x and x <= line_max_x and line_min_y <= y and y <= line_max_y:
        return True
    else:
        return False


def add_street(estreet={}, estreet_name=[], estreet_gps=[]):
    """
    add a street to the dictionary
    :param estreet: the dictionary of streets{name: gps}
    :param estreet_name: the array of street name
    :param estreet_gps: the array of street gps
    :return: updated estreet
    """
    estreet[estreet_name]=estreet_gps


def change_street(estreet={}, estreet_name=[], estreet_gps=[]):
    """
    change a street in the dictionary
    :param estreet:
    :param estreet_name:
    :param estreet_gps:
    :return:
    """
    estreet[estreet_name]=estreet_gps


def remove_street(estreet={}, estreet_name=[]):
    """
    remove a street from the dictionary
    :param estreet:
    :param estreet_name:
    :return:
    """
    del estreet[estreet_name]


def generate_graph(estreet={},oldV= {},Vcounter = 0):
    """
    generate the undirected graph V,E
    :param estreet: input street name and gps {"name1":[(),()],"name2":[(),(),()]}
    :return: V dictionary, E set, old V dictionary
    """
    ee = set([])# the set of edges
    ev = {}# the dictionary of V reverse,i.e {gps:vertex id}
    estreet_line = Create_line(estreet)
    old_line = []
    ev_reverse={} # the dictionary of V,i.e {vertex_id,gps}
    ev_reverse_f = {} #format all float
    vpoint = set([])

    for each_street in estreet_line:
        old_line.append(each_street)
        new_line = list(set(estreet_line) - set(old_line))
        if new_line:
            for each_seg in estreet_line[each_street]:
                for each_new_street in new_line:
                    for each_seg_new in estreet_line[each_new_street]:
                        intersection = line_intersection(each_seg, each_seg_new)
                        if intersection:
                            for new_v in [each_seg[0],each_seg[1],each_seg_new[0],each_seg_new[1],intersection]:
                                if not new_v in ev:
                                    if new_v in oldV:
                                        ev[new_v] = oldV[new_v]
                                        ev_reverse[oldV[new_v]] = new_v
                                    else:
                                        ev[new_v] = Vcounter
                                        ev_reverse[Vcounter] = new_v
                                        Vcounter = Vcounter + 1
                            for new_v_point in [each_seg[0],each_seg[1],each_seg_new[0],each_seg_new[1]]:
                                if new_v_point != intersection:
                                    ee.add((ev[new_v_point], ev[intersection]))
                                    vpoint.add(new_v_point)

    for each_vpoint in vpoint:
        vpoint_edge = set([])
        point_counter = 0
        dis_point_ins = []

        for each_e in ee:
            if ev_reverse[each_e[0]] == each_vpoint:
                point_counter = point_counter + 1
                vpoint_edge.add(each_e)

        if point_counter > 1:# there are more than 1 intersections on a segment
            dis_counter = 0
            dis_v_dic = {}
            for each_e_ins in vpoint_edge:
                dis_point_ins.append(cal_distance_points_2(each_vpoint,ev_reverse[each_e_ins[1]]))# compare the distance between a point and different intersection
                dis_v_dic[dis_point_ins[dis_counter]] = ev_reverse[each_e_ins[1]]
                dis_counter = dis_counter+1
            dis_point_ins.sort()

            for del_e_ins in dis_point_ins[1:len(dis_point_ins)]:#delete an edge if there is a vertex on it
                ee.remove((ev[each_vpoint],ev[dis_v_dic[del_e_ins]]))

            for add_e_ins_i in range(0, len(dis_point_ins)-1):#add an edge between two intersections that are reachable directly
                if not (ev[dis_v_dic[dis_point_ins[add_e_ins_i+1]]],ev[dis_v_dic[dis_point_ins[add_e_ins_i]]]) in ee:
                    ee.add((ev[dis_v_dic[dis_point_ins[add_e_ins_i]]],ev[dis_v_dic[dis_point_ins[add_e_ins_i+1]]]))
    for each_new_v in ev:
        if not each_new_v in oldV:
            oldV[each_new_v] = ev[each_new_v]

    for each_rev in ev_reverse:
        ev_reverse_f[each_rev] = tuple((pp(ev_reverse[each_rev][0]), pp(ev_reverse[each_rev][1])))
    return ev_reverse_f, ee, oldV


def output_E(edge = {}):
    """
    output edge according to the standards
    :param edge: set of edge
    :return:
    """
    e_lis = list(edge)
    e_str = str(e_lis)
    e_comma = re.sub(r',\s*(?![^()]*\))', ',\n', e_str)
    e_left_bracket = re.sub(r'[(]', '<', e_comma)
    e_right_bracket = re.sub(r'[)]', '>', e_left_bracket)
    e_move_left = e_right_bracket.replace('[', '')
    e_move_right = e_move_left.replace(']', '')
    if e_move_right == '':
        print "E = {"
        print "}"
    else:
        print "E = {"
        print e_move_right
        print "}"


def output_V(Vertex = {}):
    """
    output vertex according to the standards
    :param Vertex: vertex dictionary
    :return:
    """
    v_str = str(Vertex)
    v_comma = re.sub(r',\s*(?![^()]*\))', '\n', v_str)
    v_bracket = v_comma.replace('{','')
    v_r_bracket = v_bracket.replace('}','')
    v_quotation_dele = v_r_bracket.replace("'",'')
    if v_quotation_dele == '':
        print "V = {"
        print "}"
    else:
        print "V = {"
        print v_quotation_dele
        print "}"


def pp(x):
    if isinstance(x, float):
        if x.is_integer():
            return str(int(x))
        else:
            return '{0:.2f}'.format(x)
    else:
        return str(x)


def main():

    # create a street dictionary
    ori_street_dic = {}
    old_street_dic = {}
    v_id = 0
    pattern_a = re.compile(r'^\ *a\ +"[A-Za-z\ ]+"\ +(\(\ *\-*[0-9]+\ *,\ *\-*[0-9]+\ *\)\ *)+$')
    pattern_c = re.compile(r'^\ *c\ +"[A-Za-z\ ]+"\ +(\(\ *\-*[0-9]+\ *,\ *\-*[0-9]+\ *\)\ *)+$')
    pattern_r = re.compile(r'^\ *r\ +"[A-Za-z\ ]+"\ *$')
    pattern_g = re.compile(r'^\ *g\ *$')

    while True:
        try:
            line = sys.stdin.readline().strip('\n')
            if line == '':
                break
            if pattern_a.match(line):
                gps_street = []
                name_street = re.search(r'"(.*)"',line).group().lower()
                gps_raw = re.findall(r'\(([0-9\-,]+)\)',line)
                for i in gps_raw:
                    gps_toast = eval(i)
                    gps_street.append(gps_toast)
                add_street(ori_street_dic,name_street,gps_street)
            elif pattern_c.match(line):
                name_street = re.search(r'"(.*)"', line).group().lower()
                if name_street in ori_street_dic:
                    gps_street = []
                    gps_raw = re.findall(r'\(([0-9\-,]+)\)', line)
                    for i in gps_raw:
                        gps_toast = eval(i)
                        gps_street.append(gps_toast)
                    change_street(ori_street_dic,name_street,gps_street)
                else:
                    print "Error: 'c' specified for a street that does not exist."
            elif pattern_r.match(line):
                name_street = re.search(r'"(.*)"', line).group().lower()
                if name_street in ori_street_dic:
                    remove_street(ori_street_dic,name_street)
                else:
                    print "Error: 'r' specified for a street that does not exist."
            elif pattern_g.match(line):
                V,E,old_street_dic = generate_graph(ori_street_dic,old_street_dic,v_id)
                v_id = v_id + len(V)
                output_V(V)
                output_E(E)
            else:
                raise Exception("Error: Input is wrong!")
        except:
            print 'Error: Input is wrong!'
    print 'Finished reading input'

    # return exit code 0 on successful termination
    sys.exit(0)

if __name__ == '__main__':
    main()
