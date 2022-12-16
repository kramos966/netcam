from src import CameraViewer

def main():
    w, h = 1024, 768
    vis = CameraViewer(w, h)
    vis.mainloop()

if __name__ == "__main__":
    main()
