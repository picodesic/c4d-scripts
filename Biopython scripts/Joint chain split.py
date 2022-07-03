import c4d
from c4d import gui
# Welcome to the world of Python


# The selected objects are the two joints where the split will happen
# Trying to maintain relationship to single point cloud and weight tag

# Main function
def main():
    joint_split = doc.GetActiveObjects(1)  # Include children
    head_1, head_2 = joint_split
    if head_2.GetUp() == head_1:
        reverse_half = []
        joint = head_1
        parent = joint.GetUp()
        while parent.IsInstanceOf(c4d.Ojoint):
            reverse_half.append(joint)
            parent = parent.GetUp()
        print reverse_half



# Execute main()
if __name__=='__main__':
    main()