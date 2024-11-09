Function StripHarakat(text As String) As String
    Dim i As Integer
    Dim result As String
    Dim charCode As Long
    
    result = ""
    
    ' Loop through each character in the text
    For i = 1 To Len(text)
        charCode = AscW(Mid(text, i, 1))
        
        ' Skip if the character is a haraka (Unicode range: 0x064B to 0x0652)
        If charCode < &H64B Or charCode > &H652 Then
            result = result & Mid(text, i, 1)
        End If
    Next i
    
    StripHarakat = result
End Function

Function LevenshteinDistance(str1 As String, str2 As String) As Integer
    Dim i As Integer, j As Integer
    Dim cost As Integer
    Dim len1 As Integer, len2 As Integer
    Dim d() As Integer
    
    len1 = Len(str1)
    len2 = Len(str2)
    
    ReDim d(0 To len1, 0 To len2)
    
    For i = 0 To len1
        d(i, 0) = i
    Next i
    For j = 0 To len2
        d(0, j) = j
    Next j
    
    For i = 1 To len1
        For j = 1 To len2
            If Mid(str1, i, 1) = Mid(str2, j, 1) Then
                cost = 0
            Else
                cost = 1
            End If
            d(i, j) = Application.WorksheetFunction.Min(d(i - 1, j) + 1, _
                                                         d(i, j - 1) + 1, _
                                                         d(i - 1, j - 1) + cost)
        Next j
    Next i
    
    LevenshteinDistance = d(len1, len2)
End Function

Function SimilarityScore(correctText As String, generatedText As String) As Double
    Dim maxLen As Integer
    Dim editDistance As Integer
    Dim similarity As Double
    
    maxLen = Application.WorksheetFunction.Max(Len(correctText), Len(generatedText))
    editDistance = LevenshteinDistance(correctText, generatedText)
    
    ' Calculate similarity as a decimal (0 to 1 range)
    similarity = (1 - (editDistance / maxLen))
    SimilarityScore = Round(similarity, 4) ' Returns a result like 0.9500 for 95%
End Function

