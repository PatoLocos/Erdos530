# Sidon experiment: measure ℓ(N) for various N
# Using greedy algorithm as lower bound

$data = @()
foreach ($N in @(10,20,30,40,50,60,70,80,90,100,150,200,300,500,1000)) {
    $sums = @{}
    $S = @()
    foreach ($x in 1..$N) {
        $ok = $true
        foreach ($y in $S) {
            if ($sums.ContainsKey($x + $y)) { $ok = $false; break }
        }
        if ($ok -and -not $sums.ContainsKey($x + $x)) {
            foreach ($y in $S) { $sums[$x + $y] = $true }
            $sums[$x + $x] = $true
            $S += $x
        }
    }
    $ratio = [Math]::Round($S.Count / [Math]::Sqrt($N), 4)
    $data += [PSCustomObject]@{
        N = $N
        SidonSize = $S.Count
        Ratio = $ratio
        SqrtN = [Math]::Round([Math]::Sqrt($N), 2)
    }
}

$data | Format-Table -AutoSize
$data | Export-Csv -Path "D:\Erdos\experiments\sidon_data.csv" -NoTypeInformation
