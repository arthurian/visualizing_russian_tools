from django.contrib import admin
from .models import Lemma, Inflection

@admin.register(Lemma)
class LemmaAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'lemma', 'translation', 'pos', 'pos_subtype', 'animacy', 'level', 'rank', 'aspect', 'transitivity')
    list_filter = ('level', 'pos', 'pos_subtype', 'animacy', 'aspect', 'transitivity')
    search_fields = ['id', 'lemma', 'translation']

@admin.register(Inflection)
class InflectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'form', 'category', 'description')
    list_filter = ('category',)
    autocomplete_fields = ('lemma', )
    search_fields = ['form']