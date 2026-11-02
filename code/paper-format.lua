-- Preserve appendix numbering and code glyphs in both journal formats.
function Pandoc(doc)
  if FORMAT:match("commonmark") or FORMAT:match("gfm") then
    return doc:walk({
      Para = function(paragraph)
        local markdown = pandoc.write(pandoc.Pandoc({paragraph}), "commonmark", {wrap_text = "none"})
        -- Older Quarto versions expand metadata in badge URLs after link parsing.
        if markdown:find("badge") and markdown:find("\\%[") then
          markdown = markdown:gsub("\\%[", "["):gsub("\\%]", "]"):gsub("\\!", "!")
          return pandoc.RawBlock("markdown", markdown)
        end
      end
    })
  end
  local appendix = 0
  local current_number = nil
  local current_letter = nil
  local labels = {}
  local latex = quarto.doc.is_format("latex")
  if latex then
    -- Latin Modern Mono lacks the lambda used by Julia's keyword arguments.
    -- Use the text font for that glyph so PDF copy-and-paste preserves lambda.
    quarto.doc.include_text("in-header", [[
\usepackage{newunicodechar}
\newunicodechar{λ}{{\normalfont\char"03BB}}
]])
  end

  doc = doc:walk({
    Header = function(header)
      local first_appendix = false
      if header.level == 1 and header.classes:includes("appendix") then
        appendix = appendix + 1
        current_number = header.attributes.number
        current_letter = string.char(64 + appendix)
        first_appendix = appendix == 1
      end

      if current_letter then
        local number = header.attributes.number
        if number and current_number then
          local suffix = number:sub(#current_number + 1)
          local label = current_letter .. suffix
          labels[header.identifier] = label
          header.attributes.number = label
          if not latex then
            for _, inline in ipairs(header.content) do
              if inline.t == "Span" and inline.classes:includes("header-section-number") then
                inline.content = pandoc.Inlines({pandoc.Str(label)})
                break
              end
            end
          end
        end
      end

      if latex and first_appendix then
        return {pandoc.RawBlock("latex", "\\appendix"), header}
      end
      return header
    end
  })

  return doc:walk({
    Link = function(link)
      local label = labels[link.target:match("^#(.+)$")]
      if label and link.classes:includes("quarto-xref") then
        link.content = pandoc.Inlines({pandoc.Str("Appendix"), pandoc.Space(), pandoc.Str(label)})
        return link
      end
    end,
    Inlines = function(inlines)
      if latex then
        for index, inline in ipairs(inlines) do
          if inline.t == "RawInline" and inline.format == "latex" then
            local identifier = inline.text:match("^\\ref{([^}]+)}$")
            if identifier and labels[identifier] and index > 2 then
              local prefix = inlines[index - 2]
              if prefix.t == "Str" and prefix.text == "Section" then
                prefix.text = "Appendix"
              end
            end
          end
        end
        return inlines
      end
    end
  })
end
