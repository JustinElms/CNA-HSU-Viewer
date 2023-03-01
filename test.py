import sys

from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout


from components.filter_list import FilterList


def changed(item1, item2):
    print(item1, item2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = QWidget()
    main.setFixedSize(600, 600)
    layout = QHBoxLayout(main)
    list = FilterList(main, changed)

    # list.set_items(
    #     ["item 1", "item 2", "item 3", "item 4", "item 5", "item 6"]
    # )

    list.set_items(
        {
            "cat1": [
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
            ],
            "cat2": [
                "item 1",
                "item 2",
                "item 3",
                "item 4",
                "item 5",
                "item 6",
            ],
        }
    )
    layout.addWidget(list)
    main.show()
    # ex = main()
    app.exec()
