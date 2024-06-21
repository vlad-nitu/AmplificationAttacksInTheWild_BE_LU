from visualiser_boxplot_vendor_or_product_DNS_base import preprocess_data, draw_boxplot

if __name__ == "__main__":
    box_plots = preprocess_data('vendor', 6)
    draw_boxplot('vendor', box_plots)

