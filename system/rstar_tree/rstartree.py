import rstar_tree.rectangle as rct

class RStarTree:
    def __init__(self, children=[], point_data={}, is_leaf=None):
        """
        Spatially index point data
        ---------------------------------
        Parameters:
        -----------
        children: The subtrees which determine the key rectangle

        point_data: a dictionary where keys are point ids, values are lists of
        point coordinates.
        """
        if is_leaf is not None:
            self.is_leaf = is_leaf
        else:
            # Tự động xác định là nút lá nếu có dữ liệu điểm nhưng không có children
            self.is_leaf = bool(point_data and not children)

        self.is_null = not (point_data or children)

        if point_data:
            if children:
                raise ValueError
            else:
                self.is_leaf = True
                self.is_null = False
        else:
            if not children:
                self.is_leaf = False
                self.is_null = True
            else:
                self.is_leaf = False
                self.is_null = False

        self.children = children
        self.points = point_data

        self.update_bounding_rectangle()


    def __eq__(self, other):
        # check that children/point data is the same?
        return self.key == other.key and self.is_leaf == other.is_leaf


    def __str__(self):
        return str(self.key)


    def get_child_count(self):
        return len(self.children)


    def get_child_rectangles(self):
        return [child.key for child in self.children]


    def get_point_count(self):
        return len(self.points)


    def get_points(self):
        # return list(self.points.values())
        return [value[0] for value in self.points.values()]


    def does_point_to_leaves(self):
        blist = [child.is_leaf for child in self.children]
        return all(blist)


    def update_bounding_rectangle(self):
        if self.is_leaf:
            P = self.get_points()
            new_key = rct.bounding_box_points(P)
        elif self.is_null:
            new_key = rct.EmptyRectangle(1)
        else:
            R = self.get_child_rectangles()
            if R:
                new_key = rct.bounding_box(R)
            else:
                new_key = rct.EmptyRectangle(1)
        self.key = new_key

    def update_tree_bounding_rectangle(self):
        count_child = len(self.children)
        if(count_child>0):
            for i in range(count_child):
                self.children[i].update_tree_bounding_rectangle()
        
        self.update_bounding_rectangle()
       

    def add_point_data(self,point_key,point_value, point_extend):
        if self.is_leaf:
            self.points[point_key]=(point_value,point_extend)
            self.update_bounding_rectangle()
        else:
            pass

    def remove_point_data(self,point_key):
        if self.is_leaf:
            del self.points[point_key]
            self.update_bounding_rectangle()
        else:
            pass


    def add_child(self,rt):
        self.children.append(rt)
        self.update_bounding_rectangle()


    def remove_child(self,rt):
        self.children.remove(rt)
        self.update_bounding_rectangle()

    def print_structure(self, level=0):
        """
        In ra cấu trúc của cây R*-Tree bằng cách duyệt qua các nút.
        """
        indent = "  " * level
        if self.is_leaf:
            print(f"{indent}Leaf Node: Bounding Rectangle = {self.key}, Points = {self.points}")
        else:
            print(f"{indent}Internal Node: Bounding Rectangle = {self.key}, Children count = {len(self.children)}")
            for child in self.children:
                child.print_structure(level + 1)


NullRT = RStarTree()



def overlap_enlargement_required(rt, candidate, entry):
    """

    """
    rects = rt.get_child_rectangles()
    rects.remove(candidate.key)
    enlarged_rect = candidate.key.union(entry)

    result = 0.0
    for r in rects:
        result += enlarged_rect.intersection_volume(r)
    return result


def volume_enlargement_required(candidate, entry):
    """
    """
    rect = candidate.key
    vol0 = rect.volume()
    rect = rect.union(entry)
    vol1 = rect.volume()
    return vol1 - vol0


def is_descendant(rt,rtq):
    """
    Discern whether rtq descends from rt.
    -------------------------------------
    """
    if rt == rtq:
        return True

    R = rt.key
    RQ = rtq.key
    if (not R.is_proper_superset(RQ)) or rt.is_leaf:
        return False

    candidates = [ch for ch in rt.children if ch.key.is_proper_superset(RQ)]
    if not candidates:
        return False
    else:
        return any(is_descendant(ch, rtq) for ch in candidates)


def path_to_subtree(rt_from, rt_to, path=[]):
    """
    Get path from tree rt_from to subtree rt_to:
    --------------------------------------------
    Parameters:
    -----------
    rt_from: the starting node
    rt_to: the subtree of interest
    path: the path traversed thus far

    Returns:
    --------
    updated_path: [rt_from, ..., rt_to]
    """
    updated_path = path + [rt_from]

    if rt_from == rt_to:
        return updated_path

    R = rt_to.key
    candidates = [ch for ch in rt_from.children if ch.key.is_proper_superset(R)]
    if not candidates:
        #TODO: raise error?
        return []
    else:
        try:
            t = next(ch for ch in candidates if is_descendant(ch, rt_to))
        except StopIteration:
            return updated_path
        return path_to_subtree(t, rt_to, updated_path)


def choose_subtree(rt, lvl, entry):
    """
    Chooses subtree in rt for inserting entry
    -----------------------------------------
    Parameters:
    -----------
    rt: R*-tree in which entry will be inserted
    lvl: level of node rt. 0 means root level.
    entry: rectangle to be inserted. may be a point rectangle.

    Returns:
    --------
    rt: the chosen subtree
    lvl: the level of the chosen subtree
    """
    if rt.is_leaf:
        return rt, lvl
    if rt.does_point_to_leaves():
        keyfunc = lambda child: (overlap_enlargement_required(rt, child, entry),
        volume_enlargement_required(child,entry), child.key.volume())

        t = min(rt.children, key = keyfunc)
        # should resolve ties by choosing candidate whose volume needs to be
        # enlarged the least. resolve those ties by choosing the rectangle of
        # smallest volume.
        # there may be multiple candidates whose accomodating the entry would
        # not cause any overlap enlargement
    else:
        keyfunc = lambda child: (volume_enlargement_required(child,entry),
        child.key.volume())

        t = min(rt.children, key = keyfunc)
    return choose_subtree(t, lvl + 1, entry)


class RTCursor:
    def __init__(self,rt, M, m, p):
        # level: overflow_was_treated
        self.level_actions = {0:False}
        self.root = rt
        self.M = M
        self.m = m
        self.p = p


    def insert(self, point_data, point_extend):
        """
        We will only be indexing points.
        """
        self._insert_point(self.root, 0, point_data, point_extend)
        self.level_actions = {0:False}


    def _insert_point(self, rt, rt_lvl, point_data, point_extend):
        P_id, P = point_data
        E = rct.Rectangle(P,P)

        st, lvl = choose_subtree(rt, rt_lvl, E)

        # path = path_to_subtree(rt,st)
        path = path_to_subtree(self.root, st)
        point_count = st.get_point_count()
        if point_count < self.M:
            st.add_point_data(P_id, P, point_extend)
            self.update_bounding_rectangle()
        elif lvl != 0:
            # overflow not at root

            # set predecessor to next to last element of path
            #st_pred = path[-2]
            if len(path) > 1:
                st_pred = path[-2]
            else:
                st_pred = NullRT  # Hoặc đặt giá trị mặc định khác nếu cần
            # add the point and then treat the overflow
            st.add_point_data(P_id, P, point_extend)
            self.update_bounding_rectangle()
            caused_split = self.overflow_treatment(st,lvl,st_pred)
            if caused_split and st_pred.get_child_count() > self.M:
                
                # Propagate overflow treatment up the insertion path
                # print('pointdata: ', P_id, P)
                # print('root')
                # print_rstree(self.root)
                _ = self.propagate_overflow_treatment(lvl - 1, path)
                
        else:
            # overflow at root
            st.add_point_data(P_id, P, point_extend)
            self.update_bounding_rectangle()
            _ = self.overflow_treatment(st, lvl, NullRT)
        # Make sure all covering rectangles in insertion path are adjusted
        # to be minimum bounding rectangles


    # def _insert_node(self, rt, rt_lvl, t):
    #     # nếu node t là lá
    #     if(t.is_leaf):
    #         for k in t.points:
    #             self._insert_point(self.root, rt_lvl+1, (k, t.points[k]))
    #     else:  #nếu t không phải là lá
    #         for node in t.children:
    #             self._insert_node(self.root, rt_lvl, node)

    def split_leaf(self, t, pred):
        count = t.get_point_count()
        # print(f"Debug: count = {count}, M = {self.M}")
        assert count == self.M + 1
        ax = choose_split_axis_leaf(t, self.M, self.m)
        idx = choose_split_index_leaf(t, ax, self.M, self.m)

        kf = lambda k: (t.points[k][0])[ax]
        sorted_along_axis = sorted(list(t.points), key = kf) #########################################################

        # point data for the two new leaves
        group_1 = {x: t.points[x] for x in sorted_along_axis[0:idx]}
        group_2 = {x: t.points[x] for x in sorted_along_axis[idx:]}

        # instantiate the new leaves
        new_leaf_1 = RStarTree(children=[],is_leaf=True,point_data=group_1)
        new_leaf_2 = RStarTree(children=[],is_leaf=True,point_data=group_2)

        if pred == NullRT:
            new_root = RStarTree(children = [new_leaf_1, new_leaf_2], is_leaf=False)
            self.root = new_root
        else:
            # delete original leaf
            pred.remove_child(t)
            self.update_bounding_rectangle()

            # add the new leaves to the predecessor
            pred.add_child(new_leaf_1)
            self.update_bounding_rectangle()
            pred.add_child(new_leaf_2)
            self.update_bounding_rectangle()



    def split_node(self, t, pred):
        count = t.get_child_count()
        assert count == self.M + 1
        ax = choose_split_axis(t, self.M, self.m)
        idx, islower = choose_split_index(t, ax, M=self.M, m=self.m)

        kf = lambda ch: ch.key.minima[ax]
        sorted_along_axis = sorted(t.children, key = kf)

        # children for two new nodes
        group_1 = sorted_along_axis[0:idx]
        group_2 = sorted_along_axis[idx:]

        # instantiate new nodes
        node_1 = RStarTree(children=group_1, is_leaf=False)
        node_2 = RStarTree(children=group_2, is_leaf=False)

        if pred == NullRT:
            # make new root?
            new_root = RStarTree(children = [node_1, node_2], is_leaf=False)
            self.root = new_root
        else:
            # delete original node
            
            pred.remove_child(t)
            self.update_bounding_rectangle()

            # add back nodes
            pred.add_child(node_1)
            self.update_bounding_rectangle()
            pred.add_child(node_2)
            self.update_bounding_rectangle()


    def overflow_treatment(self, rt, lvl, pred):
        split_performed = False

        if lvl not in self.level_actions:
            self.level_actions[lvl] = False

        # if not the root and not already called at this level
        if (lvl != 0) and (not self.level_actions[lvl]):
            self.level_actions[lvl] = True
            split_performed = False
            if rt.is_leaf:
                self.leaf_re_insert(rt, lvl)
            else:
                split_performed = True
                self.split_node(rt, pred)

        else:
            split_performed = True
            if rt.is_leaf:
                self.split_leaf(rt, pred)
            else:
                self.split_node(rt, pred)
        return split_performed

######################################################################################################################
    def leaf_re_insert(self, rt, lvl):
        """
        Called on overflowing (M+1 entries) leaf
        """
        # Get a list of points' keys ordered by points' distances from the center
        # of leaf's rectangle, descending
        # print('rt')
        # print_rstree(rt)
        keyfunc = lambda k: rct.point_to_center_distance_squared(rt.points[k][0], rt.key)
        pts_by_dist = sorted(list(rt.points), key=keyfunc, reverse=True)

        # Slate the p points most distant from the center to be removed from rt
        to_remove = pts_by_dist[0:self.p]

        # Prepare (key, value) pairs to be reinserted
        to_re_insert = [((k, rt.points[k][0]), rt.points[k][1]) for k in to_remove]

        # Remove the chosen points, updating leaf's bounding rectangle
        for pk in to_remove:
            rt.remove_point_data(pk)
            self.update_bounding_rectangle()

        # close reinsert: because the tree depends on the order of insert
        # inserting pts closer to the center first performs differently
        to_re_insert.reverse()

        # Iteratively reinsert entries
        for pt_data, pt_extend in to_re_insert:
            self._insert_point(rt, lvl, pt_data, pt_extend)


    # def node_re_insert(self, rt, lvl):
    #     """
    #     Called on overflowing (M+1 entries) non-leaf node
    #     """
    #     # Get a list of children sorted by their centers' distances from the
    #     # center of the node's rectangle, descending.
    #     node_rect = rt.key
    #     keyfunc = lambda cr: node_rect.center_distance_squared(cr.key)
    #     # children_by_dist = sorted(children, key=keyfunc, reverse=True)
    #     children_by_dist = sorted(rt.children, key=keyfunc, reverse=True)
    #     # Slate first p points to be removed and reinserted
    #     to_remove = children_by_dist[0:p]
    #     # close reinsert
    #     # print('len(to_remove)', len(to_remove))
    #     # to_re_insert = to_remove.reverse()
    #     to_re_insert = list(to_remove)
    #     # print('len(to_re_insert)', len(to_re_insert))
    #     # Remove them, updating node's bounding rectangle
    #     for c in to_remove:
    #         rt.remove_child(c)
    #         self.update_bounding_rectangle()
    #     for c in to_re_insert[::-1]: 
    #         self._insert_node(rt,lvl,c)


    def propagate_overflow_treatment(self, lvl, node_list):
        was_root_split = False
        for i in reversed(range(len(node_list))):
            t = node_list[i]  
            count = t.get_child_count()
            if count > self.M:
                if i >= 1:
                    pred = node_list[i-1]
                    
                    _ = self.overflow_treatment(t, lvl, pred)
                    
                else:
                    pred = NullRT
                    # print('covaodyak')
                    was_root_split = self.overflow_treatment(t, lvl, pred)
            lvl -= 1
        return was_root_split

    def update_bounding_rectangle(self):
        self.root.update_tree_bounding_rectangle()
            

def choose_split_axis_leaf(t, M, m):
    d = t.key.dimension
    margins = []
    for i in range(0,d):
        kf = lambda k: (t.points[k][0])[i]
        sorted_by_i = sorted(list(t.points), key = kf)

        S_i = 0.0
        for j in range(1, M - 2*m + 2):
            first_split_group = sorted_by_i[0:(m - 1 + j)]
            bb_1 = rct.bounding_box_points([t.points[k][0] for k in first_split_group])

            second_split_group = sorted_by_i[(m - 1 + j):]
            bb_2 = rct.bounding_box_points([t.points[k][0] for k in second_split_group])

            S_i += rct.rectangle_perimeter(bb_1) + rct.rectangle_perimeter(bb_2)
        margins.append((S_i,i))

    return (min(margins))[1]


def choose_split_index_leaf(t,axis, M, m):
    kf = lambda k: (t.points[k][0])[axis]
    sorted_along_axis = sorted(list(t.points), key = kf)

    scores = []
    for j in range(1, M - 2*m + 2):
        first_split_group = sorted_along_axis[0:(m - 1 + j)]
        bb_1 = rct.bounding_box_points([t.points[k][0] for k in first_split_group])

        second_split_group = sorted_along_axis[(m - 1 + j):]
        bb_2 = rct.bounding_box_points([t.points[k][0] for k in second_split_group])

        overlap_j = bb_1.intersection_volume(bb_2)
        vol_score_j = bb_1.volume() + bb_2.volume()

        scores.append((overlap_j,vol_score_j, m - 1 + j))

    return (min(scores))[2]


def choose_split_axis(t, M, m):
    d = t.key.dimension
    child_rects = t.get_child_rectangles()

    margins = []
    for i in range(0,d):
        lower_kf = lambda ch: ch.minima[i]
        by_lower_i = sorted(child_rects, key = lower_kf)

        upper_kf = lambda ch: ch.maxima[i]
        by_upper_i = sorted(child_rects, key = upper_kf)

        S_i = 0.0
        for j in range(1, M - 2*m + 2):
            g1 = by_lower_i[0:(m - 1 + j)]
            g2 = by_lower_i[(m - 1 + j):]
            g3 = by_upper_i[0:(m - 1 + j)]
            g4 = by_upper_i[(m - 1 + j):]
            margin_1 = rct.rectangle_perimeter(rct.bounding_box(g1))
            margin_2 = rct.rectangle_perimeter(rct.bounding_box(g2))
            margin_3 = rct.rectangle_perimeter(rct.bounding_box(g3))
            margin_4 = rct.rectangle_perimeter(rct.bounding_box(g4))
            S_i += margin_1 + margin_2 + margin_3 + margin_4

        margins.append((S_i, i))

    return (min(margins))[1]


def choose_split_index(t,axis, M, m):
    child_rects = t.get_child_rectangles()

    lower_kf = lambda ch: ch.minima[axis]
    by_lower = sorted(child_rects, key = lower_kf)

    upper_kf = lambda ch: ch.maxima[axis]
    by_upper = sorted(child_rects, key = upper_kf)

    scores = [] # will hold tuples (overlap, volume, index, is_lower)
    for j in range(1, M - 2*m + 2):
        bb_1 = rct.bounding_box(by_lower[0:(m - 1 + j)])
        bb_2 = rct.bounding_box(by_lower[(m - 1 + j):])

        overlap_lower = bb_1.intersection_volume(bb_2)
        vol_score_lower = bb_1.volume() + bb_2.volume()

        scores.append((overlap_lower,vol_score_lower, m - 1 + j, True))

        bb_3 = rct.bounding_box(by_upper[0:(m - 1 + j)])
        bb_4 = rct.bounding_box(by_upper[(m - 1 + j):])

        overlap_upper = bb_3.intersection_volume(bb_4)
        vol_score_upper = bb_3.volume() + bb_4.volume()

        scores.append((overlap_upper, vol_score_upper, m - 1 + j, False))

    best = min(scores, key = lambda s: (s[0], s[1]))
    return best[2], best[3]


def print_rstree(root, level = 1, order = 1):
    print('\t'*(level-1), '-'*20)
    print('\t'*(level-1), 'NÚT CẤP ', level, ' THỨ ', order)
    print('\t'*(level-1), root)
    print('\t'*(level-1), 'Số lượng con: ', len(root.children))
    if(root.is_leaf):
        print('\t'*(level-1), 'Số lượng điểm ở trong nút này: ', [(point[0], point[1]) for point in root.points.values()])
    childs = len(root.children)
    for i in range(childs):
        print_rstree(root.children[i], level+1, i+1)

def create_tree_from_pts(pts_tuples, M=4, m=2, p=1, print_output=True):
    """
    Tạo cây từ các điểm và cập nhật MBB cho gốc.
    """
    # pt_dict = {k: v for k, v in pts_tuples[0:M-1]}
    # print(pts_tuples)
    pt_dict = {k: (v[0:3], v[3:5]) for k, v in pts_tuples[0:M-1]}
    print(pt_dict)
    starting_node = RStarTree(children=[], point_data=pt_dict, is_leaf=True)
    retv = RTCursor(starting_node, M=M, m=m, p=p)
    # print('start: ')
    # print_rstree(starting_node)
    # i = M-1
    for k, v in pts_tuples[M-1:]:
        point_data=(k, v[0:3])
        point_extend = v[3:5]
        retv.insert(point_data,point_extend )
        # print('*'*20)
        # print('thêm phần tử thứ ', i+1)
        # i = i+1

    retv.root.update_bounding_rectangle()
    # print(print_output)
    if(print_output):
        print('Cấu trúc cây:')
        print_rstree(retv.root)
    return retv

