from src import CameraViewer

def main():
    w, h = 800, 600
    vis = CameraViewer(w, h, fullscreen=False)
    vis.mainloop()

if __name__ == "__main__":
    main()
