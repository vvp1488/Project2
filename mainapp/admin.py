from django.contrib import admin

from .models import *
from django.forms import ModelChoiceField, ModelForm
from PIL import Image
from django.utils.safestring import mark_safe


class SmartphoneAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        # if not instance.sd:
        #     self.fields['sd_volume_max'].widget.attrs.update({
        #         'readonly': True,
        #         'style': 'background : lightgrey;'
        #     })

    def clean(self):
        if not self.cleaned_data['sd']:
            self.cleaned_data['sd_volume_max'] = None
        return self.cleaned_data


class NotebookAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].help_text = 'Обязательное поле для заполнения'
        self.fields['image'].help_text = mark_safe(
            '<div style="color:red; font-size:14px" >Загружайте изображения с минимальный разрешением {}x{}</div>'.format(
                *Product.MIN_RESOLUTION))

    # def clean_image(self):
    #     image = self.cleaned_data['image']
    #     img = Image.open(image)
    #     min_width, min_height = Product.MIN_RESOLUTION
    #     max_width, max_height = Product.MAX_RESOLUTION
    #     if image.size > Product.MAX_IMAGE_SIZE:
    #         raise ValidationError('Больше допустимого размера - 3 мбайта')
    #     if img.width < min_width or img.height < min_height:
    #         raise ValidationError('Изображения меньше минимального разрешения')
    #     elif img.width > max_width or img.height > max_height:
    #         raise ValidationError('Изображения больше максимального разрешения')
    #
    #     return image


class NotebookAdmin(admin.ModelAdmin):
    form = NotebookAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='notebooks'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SmartphoneAdmin(admin.ModelAdmin):
    change_form_template = 'admin.html'
    form = SmartphoneAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='smartphones'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(Notebook, NotebookAdmin)
admin.site.register(Smartphone, SmartphoneAdmin)
admin.site.register(CartProduct)
admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(Order)
