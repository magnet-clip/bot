import matplotlib.pyplot as plt


class Plotter:
    @staticmethod
    def create_plot(labels, labels_val, values, png_filename, title):
        # TODO add title / legend
        failed = False
        try:
            plt.plot(labels_val, values)
            plt.xticks(labels_val, labels)
            # -----------------
            plt.autofmt_xdate()

            plt.savefig(png_filename)
        except Exception as e:
            print(e)
            failed = True
        finally:
            plt.clf()

        return failed
