m_leaf = [
    "M_EmText",
    "M_Paragraph",
    "M_Header",
    "M_Image",
    "M_Video",
    "M_Link",
    "M_Button",
    "M_Span",
    "M_Divider",
    "M_VerticalDivider",
]
m_branch = [
    "M_RepeatGroup",
    "M_1Row",
    "M_GroupGeneral",
    "M_ButtonRow",
    "M_MultiP",
    "M_TextGroup",
]
m_section = ["Section_ImgP", "Section_FullImg"]

m_root = ["M_Section", "M_Body", "M_Footer"]

m_required = [
     "M_Divider",
]

# leaf modules come first to prevent infinite loops
starter_modules = m_root + m_leaf + m_section + m_branch

standard_modules = m_leaf + m_branch
