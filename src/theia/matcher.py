from oculus import Line2D, Line2DParameters


class LineMatcher:
    def __init__(self, **kwargs):
        params = Line2DParameters()

        params.weakThreshold = kwargs.get('weakThreshold', 10.0)
        params.strongThreshold = kwargs.get('strongThreshold', 55.0)
        params.numFeatures = kwargs.get('numFeatures', 63)
        params.pyramid = kwargs.get('pyramid', (5, 8))

        self.params = params
        self.matcher = Line2D(params)

    def add_template(self, template, class_id):
        return self.matcher.addTemplate(template, class_id)

    def remove_template(self, class_id, template_id):
        self.matcher.removeTemplate(class_id, template_id)

    def remove_class(self, class_id):
        self.matcher.removeClass(class_id)

    def match(self, image, threshold):
        matches = self.matcher.match(image, threshold)
        return list(matches)

    def export_template(self, class_id, template_id):
        return self.matcher.exportTemplate(class_id, template_id)

    def import_template(self, data):
        return self.matcher.importTemplate(data)

    def export_class(self, class_id):
        return self.matcher.exportClass(class_id)

    def import_class(self, data):
        return self.matcher.importClass(data)

    def num_templates(self):
        return self.matcher.numTemplates()

    def num_classes(self):
        return self.matcher.numClasses()

    def num_templates_in_class(self, class_id):
        return self.matcher.numTemplatesInClass(class_id)
